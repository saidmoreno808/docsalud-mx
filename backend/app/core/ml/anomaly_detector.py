"""
Detector de anomalias en resultados de laboratorio usando Autoencoder.

Entrena con datos normales y detecta anomalias basandose en el
error de reconstruccion. Util para identificar valores de laboratorio
que requieren atencion medica urgente.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np

from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AnomalyResult:
    """Resultado de deteccion de anomalia."""

    is_anomaly: bool
    anomaly_score: float
    reconstruction_error: float
    threshold: float
    most_anomalous_features: list[tuple[str, float]] = field(default_factory=list)


class LabAnomalyDetector:
    """Autoencoder para deteccion de anomalias en resultados de laboratorio."""

    def __init__(self, threshold_percentile: float = 95.0) -> None:
        """Inicializa el detector.

        Args:
            threshold_percentile: Percentil del error de reconstruccion
                en datos de entrenamiento para definir el umbral de anomalia.
        """
        self.threshold_percentile = threshold_percentile
        self._model: Any = None
        self._threshold: float = 0.0
        self._input_dim: int = 0
        self._is_trained = False
        self._feature_names: list[str] = []
        self._training_mean: Optional[np.ndarray] = None
        self._training_std: Optional[np.ndarray] = None

    def build_model(self, input_dim: int) -> Any:
        """Construye el modelo Autoencoder con Keras.

        Arquitectura:
        Encoder: Input -> Dense(64,relu) -> BN -> Dropout(0.3)
                 -> Dense(32,relu) -> BN -> Dropout(0.2) -> Dense(16,relu)
        Decoder: Dense(16) -> Dense(32,relu) -> BN
                 -> Dense(64,relu) -> BN -> Dense(input_dim, sigmoid)

        Args:
            input_dim: Dimension del vector de entrada.

        Returns:
            Modelo Keras compilado.
        """
        import tensorflow as tf
        from tensorflow import keras
        from keras import layers

        self._input_dim = input_dim

        inputs = keras.Input(shape=(input_dim,))

        # Encoder
        x = layers.Dense(64, activation="relu")(inputs)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(32, activation="relu")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.2)(x)
        encoded = layers.Dense(16, activation="relu")(x)

        # Decoder
        x = layers.Dense(32, activation="relu")(encoded)
        x = layers.BatchNormalization()(x)
        x = layers.Dense(64, activation="relu")(x)
        x = layers.BatchNormalization()(x)
        decoded = layers.Dense(input_dim, activation="sigmoid")(x)

        model = keras.Model(inputs, decoded, name="lab_anomaly_autoencoder")
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=1e-3),
            loss="mse",
        )

        self._model = model
        logger.info("autoencoder_built", input_dim=input_dim, params=model.count_params())
        return model

    def train(
        self,
        normal_data: np.ndarray,
        epochs: int = 100,
        batch_size: int = 32,
        validation_split: float = 0.1,
        feature_names: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """Entrena el autoencoder con datos normales.

        Solo se entrena con datos que representan valores normales.
        El umbral de anomalia se calcula como el percentil configurado
        del error de reconstruccion en los datos de entrenamiento.

        Args:
            normal_data: Datos de entrenamiento (solo valores normales).
            epochs: Numero de epochs.
            batch_size: Tamano de batch.
            validation_split: Fraccion para validacion.
            feature_names: Nombres de las features.

        Returns:
            Diccionario con metricas de entrenamiento.
        """
        from tensorflow import keras

        if feature_names:
            self._feature_names = feature_names

        self._training_mean = np.mean(normal_data, axis=0)
        self._training_std = np.std(normal_data, axis=0) + 1e-8
        normalized = (normal_data - self._training_mean) / self._training_std

        # Escalar a [0, 1] para sigmoid output
        data_min = normalized.min(axis=0)
        data_max = normalized.max(axis=0)
        data_range = data_max - data_min + 1e-8
        scaled_data = (normalized - data_min) / data_range

        input_dim = normal_data.shape[1]
        if self._model is None:
            self.build_model(input_dim)

        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor="val_loss",
                patience=10,
                restore_best_weights=True,
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.5,
                patience=5,
                min_lr=1e-6,
            ),
        ]

        history = self._model.fit(
            scaled_data, scaled_data,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=0,
        )

        reconstructed = self._model.predict(scaled_data, verbose=0)
        reconstruction_errors = np.mean(np.square(scaled_data - reconstructed), axis=1)
        self._threshold = float(np.percentile(reconstruction_errors, self.threshold_percentile))

        self._is_trained = True
        self._data_min = data_min
        self._data_range = data_range

        final_loss = float(history.history["loss"][-1])
        val_loss = float(history.history.get("val_loss", [final_loss])[-1])
        actual_epochs = len(history.history["loss"])

        logger.info(
            "autoencoder_trained",
            epochs=actual_epochs,
            final_loss=f"{final_loss:.6f}",
            val_loss=f"{val_loss:.6f}",
            threshold=f"{self._threshold:.6f}",
        )

        return {
            "epochs_run": actual_epochs,
            "final_loss": final_loss,
            "val_loss": val_loss,
            "threshold": self._threshold,
            "training_samples": len(normal_data),
            "input_dim": input_dim,
        }

    def detect_anomalies(
        self,
        lab_results: np.ndarray,
        feature_names: Optional[list[str]] = None,
    ) -> list[AnomalyResult]:
        """Detecta anomalias en resultados de laboratorio.

        Reconstruye cada muestra, calcula MSE. Si el error supera
        el threshold calculado en entrenamiento, se marca como anomalia.

        Args:
            lab_results: Matriz de resultados (n_samples, n_features).
            feature_names: Nombres de features para reporte.

        Returns:
            Lista de AnomalyResult por muestra.
        """
        if not self._is_trained or self._model is None:
            raise RuntimeError("Model not trained. Call train() first.")

        names = feature_names or self._feature_names

        normalized = (lab_results - self._training_mean) / self._training_std
        scaled = (normalized - self._data_min) / self._data_range

        reconstructed = self._model.predict(scaled, verbose=0)
        per_feature_errors = np.square(scaled - reconstructed)
        reconstruction_errors = np.mean(per_feature_errors, axis=1)

        results: list[AnomalyResult] = []
        for i in range(len(lab_results)):
            error = float(reconstruction_errors[i])
            is_anomaly = error > self._threshold

            feature_errors = per_feature_errors[i]
            top_indices = np.argsort(feature_errors)[::-1][:5]
            most_anomalous = []
            for idx in top_indices:
                feat_name = names[idx] if idx < len(names) else f"feature_{idx}"
                most_anomalous.append((feat_name, float(feature_errors[idx])))

            results.append(AnomalyResult(
                is_anomaly=is_anomaly,
                anomaly_score=min(error / max(self._threshold, 1e-8), 10.0),
                reconstruction_error=error,
                threshold=self._threshold,
                most_anomalous_features=most_anomalous,
            ))

        n_anomalies = sum(1 for r in results if r.is_anomaly)
        logger.info(
            "anomaly_detection_completed",
            n_samples=len(lab_results),
            n_anomalies=n_anomalies,
        )

        return results

    def save(self, path: str) -> None:
        """Guarda modelo Keras y metadata.

        Args:
            path: Directorio de salida.
        """
        save_dir = Path(path)
        save_dir.mkdir(parents=True, exist_ok=True)

        if self._model:
            self._model.save(save_dir / "autoencoder_model.keras")

        metadata = {
            "threshold": self._threshold,
            "threshold_percentile": self.threshold_percentile,
            "input_dim": self._input_dim,
            "is_trained": self._is_trained,
            "feature_names": self._feature_names,
        }
        with open(save_dir / "metadata.json", "w") as f:
            json.dump(metadata, f)

        if self._training_mean is not None:
            np.save(save_dir / "training_mean.npy", self._training_mean)
            np.save(save_dir / "training_std.npy", self._training_std)
            np.save(save_dir / "data_min.npy", self._data_min)
            np.save(save_dir / "data_range.npy", self._data_range)

        logger.info("anomaly_detector_saved", path=path)

    def load(self, path: str) -> None:
        """Carga modelo y metadata.

        Args:
            path: Directorio con el modelo guardado.
        """
        from tensorflow import keras

        load_dir = Path(path)

        model_path = load_dir / "autoencoder_model.keras"
        if model_path.exists():
            self._model = keras.models.load_model(model_path)

        meta_path = load_dir / "metadata.json"
        if meta_path.exists():
            with open(meta_path, "r") as f:
                metadata = json.load(f)
            self._threshold = metadata["threshold"]
            self._input_dim = metadata["input_dim"]
            self._is_trained = metadata["is_trained"]
            self._feature_names = metadata.get("feature_names", [])

        mean_path = load_dir / "training_mean.npy"
        if mean_path.exists():
            self._training_mean = np.load(mean_path)
            self._training_std = np.load(load_dir / "training_std.npy")
            self._data_min = np.load(load_dir / "data_min.npy")
            self._data_range = np.load(load_dir / "data_range.npy")

        logger.info("anomaly_detector_loaded", path=path)
