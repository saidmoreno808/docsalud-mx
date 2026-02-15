"""
Registro centralizado de modelos ML.

Gestiona carga, versionado y seleccion de modelos para los
diferentes componentes del sistema (clasificacion, NER, anomalias).
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ModelInfo:
    """Informacion de un modelo registrado."""

    name: str
    version: str
    model_type: str  # sklearn, keras, pytorch, spacy
    path: str
    metrics: dict[str, float] = field(default_factory=dict)
    is_loaded: bool = False
    load_time_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelRegistry:
    """Registro centralizado para carga y versionado de modelos ML."""

    def __init__(self, base_path: str = "./models") -> None:
        """Inicializa el registry.

        Args:
            base_path: Directorio base donde se almacenan los modelos.
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._registry: dict[str, ModelInfo] = {}
        self._loaded_models: dict[str, Any] = {}
        self._load_registry()

    def register(
        self,
        name: str,
        version: str,
        model_type: str,
        path: str,
        metrics: Optional[dict[str, float]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> ModelInfo:
        """Registra un nuevo modelo.

        Args:
            name: Nombre unico del modelo.
            version: Version semantica.
            model_type: Tipo (sklearn, keras, pytorch, spacy).
            path: Ruta al modelo guardado.
            metrics: Metricas de evaluacion.
            metadata: Metadata adicional.

        Returns:
            ModelInfo del modelo registrado.
        """
        key = f"{name}:{version}"
        info = ModelInfo(
            name=name,
            version=version,
            model_type=model_type,
            path=path,
            metrics=metrics or {},
            metadata=metadata or {},
        )
        self._registry[key] = info
        self._save_registry()

        logger.info("model_registered", name=name, version=version, type=model_type)
        return info

    def load_model(self, name: str, version: Optional[str] = None) -> Any:
        """Carga un modelo del registry.

        Si version es None, carga la ultima version disponible.

        Args:
            name: Nombre del modelo.
            version: Version especifica. Si None, usa la mas reciente.

        Returns:
            Modelo cargado.

        Raises:
            KeyError: Si el modelo no esta registrado.
            FileNotFoundError: Si el archivo no existe.
        """
        if version is None:
            version = self._get_latest_version(name)

        key = f"{name}:{version}"
        if key in self._loaded_models:
            return self._loaded_models[key]

        if key not in self._registry:
            raise KeyError(f"Model '{key}' not found in registry.")

        info = self._registry[key]
        model_path = Path(info.path)

        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        start_time = time.perf_counter()
        model = self._load_by_type(info.model_type, str(model_path))
        load_time = int((time.perf_counter() - start_time) * 1000)

        info.is_loaded = True
        info.load_time_ms = load_time
        self._loaded_models[key] = model

        logger.info(
            "model_loaded",
            name=name,
            version=version,
            type=info.model_type,
            load_time_ms=load_time,
        )

        return model

    def get_info(self, name: str, version: Optional[str] = None) -> ModelInfo:
        """Obtiene informacion de un modelo.

        Args:
            name: Nombre del modelo.
            version: Version. Si None, usa la mas reciente.

        Returns:
            ModelInfo del modelo.
        """
        if version is None:
            version = self._get_latest_version(name)
        key = f"{name}:{version}"
        if key not in self._registry:
            raise KeyError(f"Model '{key}' not found.")
        return self._registry[key]

    def list_models(self) -> list[ModelInfo]:
        """Lista todos los modelos registrados.

        Returns:
            Lista de ModelInfo.
        """
        return list(self._registry.values())

    def list_versions(self, name: str) -> list[str]:
        """Lista versiones de un modelo.

        Args:
            name: Nombre del modelo.

        Returns:
            Lista de versiones ordenadas.
        """
        versions = []
        for key, info in self._registry.items():
            if info.name == name:
                versions.append(info.version)
        return sorted(versions)

    def unload_model(self, name: str, version: Optional[str] = None) -> None:
        """Descarga un modelo de memoria.

        Args:
            name: Nombre del modelo.
            version: Version. Si None, descarga todas.
        """
        keys_to_remove = []
        for key in self._loaded_models:
            if version:
                if key == f"{name}:{version}":
                    keys_to_remove.append(key)
            else:
                if key.startswith(f"{name}:"):
                    keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._loaded_models[key]
            if key in self._registry:
                self._registry[key].is_loaded = False

        logger.info("model_unloaded", name=name, version=version)

    def _get_latest_version(self, name: str) -> str:
        """Obtiene la version mas reciente de un modelo."""
        versions = self.list_versions(name)
        if not versions:
            raise KeyError(f"No versions found for model '{name}'.")
        return versions[-1]

    def _load_by_type(self, model_type: str, path: str) -> Any:
        """Carga modelo segun su tipo."""
        if model_type == "sklearn":
            import joblib
            return joblib.load(path)

        elif model_type == "keras":
            from tensorflow import keras
            return keras.models.load_model(path)

        elif model_type == "pytorch":
            import torch
            return torch.load(path, map_location="cpu", weights_only=False)

        elif model_type == "spacy":
            import spacy
            return spacy.load(path)

        elif model_type == "joblib":
            import joblib
            return joblib.load(path)

        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def _save_registry(self) -> None:
        """Persiste el registry a disco."""
        registry_path = self.base_path / "registry.json"
        data = {}
        for key, info in self._registry.items():
            data[key] = {
                "name": info.name,
                "version": info.version,
                "model_type": info.model_type,
                "path": info.path,
                "metrics": info.metrics,
                "metadata": info.metadata,
            }

        with open(registry_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_registry(self) -> None:
        """Carga registry desde disco."""
        registry_path = self.base_path / "registry.json"
        if not registry_path.exists():
            return

        try:
            with open(registry_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            for key, info_data in data.items():
                self._registry[key] = ModelInfo(
                    name=info_data["name"],
                    version=info_data["version"],
                    model_type=info_data["model_type"],
                    path=info_data["path"],
                    metrics=info_data.get("metrics", {}),
                    metadata=info_data.get("metadata", {}),
                )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("registry_load_error", error=str(e))
