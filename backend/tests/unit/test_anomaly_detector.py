"""
Tests unitarios para LabAnomalyDetector.
"""

import numpy as np
import pytest

from app.core.ml.anomaly_detector import AnomalyResult, LabAnomalyDetector


@pytest.fixture
def normal_data() -> np.ndarray:
    """Genera datos normales de laboratorio sinteticos."""
    rng = np.random.RandomState(42)
    n_samples = 200
    # glucosa, hemoglobina, colesterol, creatinina, trigliceridos
    data = np.column_stack([
        rng.normal(90, 10, n_samples),    # glucosa (70-100)
        rng.normal(14, 1, n_samples),     # hemoglobina (12-16)
        rng.normal(180, 20, n_samples),   # colesterol (<200)
        rng.normal(0.9, 0.1, n_samples),  # creatinina (0.7-1.2)
        rng.normal(150, 20, n_samples),   # trigliceridos (<150)
    ])
    return data


@pytest.fixture
def feature_names() -> list[str]:
    return ["glucosa", "hemoglobina", "colesterol", "creatinina", "trigliceridos"]


@pytest.fixture
def trained_detector(normal_data: np.ndarray, feature_names: list[str]) -> LabAnomalyDetector:
    """Detector ya entrenado con datos normales."""
    detector = LabAnomalyDetector(threshold_percentile=95.0)
    detector.train(normal_data, epochs=10, batch_size=32, feature_names=feature_names)
    return detector


class TestBuildModel:
    def test_builds_model(self) -> None:
        detector = LabAnomalyDetector()
        model = detector.build_model(input_dim=5)
        assert model is not None
        assert detector._input_dim == 5

    def test_model_has_correct_io(self) -> None:
        detector = LabAnomalyDetector()
        model = detector.build_model(input_dim=5)
        # Input shape: (None, 5), Output shape: (None, 5)
        assert model.input_shape == (None, 5)
        assert model.output_shape == (None, 5)

    def test_model_is_compiled(self) -> None:
        detector = LabAnomalyDetector()
        model = detector.build_model(input_dim=5)
        assert model.optimizer is not None


class TestTrain:
    def test_trains_without_error(self, normal_data: np.ndarray) -> None:
        detector = LabAnomalyDetector()
        result = detector.train(normal_data, epochs=5, batch_size=32)
        assert detector._is_trained
        assert result["epochs_run"] >= 1

    def test_sets_threshold(self, normal_data: np.ndarray) -> None:
        detector = LabAnomalyDetector()
        detector.train(normal_data, epochs=5)
        assert detector._threshold > 0

    def test_loss_converges(self, normal_data: np.ndarray) -> None:
        detector = LabAnomalyDetector()
        result = detector.train(normal_data, epochs=10)
        assert result["final_loss"] < 1.0

    def test_returns_metrics(self, normal_data: np.ndarray) -> None:
        detector = LabAnomalyDetector()
        result = detector.train(normal_data, epochs=5)
        assert "final_loss" in result
        assert "val_loss" in result
        assert "threshold" in result
        assert "training_samples" in result


class TestDetectAnomalies:
    def test_normal_data_not_flagged(
        self, trained_detector: LabAnomalyDetector, normal_data: np.ndarray
    ) -> None:
        """Datos normales no deben generar muchas anomalias."""
        results = trained_detector.detect_anomalies(normal_data[:20])
        anomaly_rate = sum(1 for r in results if r.is_anomaly) / len(results)
        # At most ~10% should be flagged as anomaly
        assert anomaly_rate < 0.3

    def test_outlier_detected(self, trained_detector: LabAnomalyDetector) -> None:
        """Valores extremos deben detectarse como anomalia."""
        outlier = np.array([[300, 5, 400, 5.0, 500]], dtype=np.float64)
        results = trained_detector.detect_anomalies(outlier)
        assert len(results) == 1
        assert results[0].is_anomaly
        assert results[0].anomaly_score > 1.0

    def test_result_structure(self, trained_detector: LabAnomalyDetector) -> None:
        sample = np.array([[90, 14, 180, 0.9, 150]], dtype=np.float64)
        results = trained_detector.detect_anomalies(sample)
        assert len(results) == 1
        result = results[0]
        assert isinstance(result, AnomalyResult)
        assert result.threshold == trained_detector._threshold
        assert result.reconstruction_error >= 0

    def test_most_anomalous_features(
        self, trained_detector: LabAnomalyDetector
    ) -> None:
        outlier = np.array([[300, 14, 180, 0.9, 150]], dtype=np.float64)
        results = trained_detector.detect_anomalies(outlier)
        assert len(results[0].most_anomalous_features) > 0
        # First feature should likely be glucosa (most deviant)
        feat_name, _ = results[0].most_anomalous_features[0]
        assert isinstance(feat_name, str)

    def test_untrained_raises(self) -> None:
        detector = LabAnomalyDetector()
        with pytest.raises(RuntimeError, match="not trained"):
            detector.detect_anomalies(np.array([[1, 2, 3, 4, 5]]))


class TestSaveLoad:
    def test_save_load_preserves_detection(
        self,
        trained_detector: LabAnomalyDetector,
        tmp_path: str,
    ) -> None:
        outlier = np.array([[300, 5, 400, 5.0, 500]], dtype=np.float64)
        original = trained_detector.detect_anomalies(outlier)

        trained_detector.save(str(tmp_path))

        loaded = LabAnomalyDetector()
        loaded.load(str(tmp_path))
        restored = loaded.detect_anomalies(outlier)

        assert original[0].is_anomaly == restored[0].is_anomaly
