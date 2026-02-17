"""
Tests unitarios para FeatureEngineer.
"""

import numpy as np
import pytest

from app.core.ml.feature_engineering import FeatureEngineer, FeatureSet, MEDICAL_KEYWORDS


@pytest.fixture
def engineer() -> FeatureEngineer:
    return FeatureEngineer(max_tfidf_features=100)


@pytest.fixture
def sample_texts() -> list[str]:
    return [
        "Metformina 850mg tabletas cada 12 horas por 30 dias diagnostico diabetes",
        "Resultados de laboratorio glucosa 126 mg/dL hemoglobina 14 g/dL",
        "Nota medica exploracion fisica signos vitales presion arterial 130/85",
        "Referencia al segundo nivel hospital de referencia tratamiento previo",
    ]


class TestExtractTextFeatures:
    def test_returns_numpy_array(self, engineer: FeatureEngineer) -> None:
        result = engineer.extract_text_features("Metformina 850mg tabletas")
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float64

    def test_empty_text_returns_zeros(self, engineer: FeatureEngineer) -> None:
        result = engineer.extract_text_features("")
        assert np.all(result == 0)

    def test_manual_features_length(self, engineer: FeatureEngineer) -> None:
        result = engineer.extract_text_features("Test text with some words")
        expected_len = 6 + len(MEDICAL_KEYWORDS)
        assert len(result) == expected_len

    def test_keyword_detection(self, engineer: FeatureEngineer) -> None:
        result = engineer.extract_text_features("diabetes glucosa metformina")
        # Keywords are after the 6 base features
        keyword_features = result[6:]
        assert sum(keyword_features) >= 3

    def test_with_fitted_tfidf(self, engineer: FeatureEngineer, sample_texts: list[str]) -> None:
        engineer.fit_text_features(sample_texts)
        result = engineer.extract_text_features(sample_texts[0])
        # Should have tfidf features + manual features
        assert len(result) > 6 + len(MEDICAL_KEYWORDS)


class TestExtractTextFeaturesBatch:
    def test_batch_shape(self, engineer: FeatureEngineer, sample_texts: list[str]) -> None:
        result = engineer.extract_text_features_batch(sample_texts)
        assert result.shape[0] == len(sample_texts)
        assert result.shape[1] > 0

    def test_auto_fits_tfidf(self, engineer: FeatureEngineer, sample_texts: list[str]) -> None:
        engineer.extract_text_features_batch(sample_texts)
        assert engineer._is_fitted


class TestExtractPatientFeatures:
    def test_returns_correct_shape(self, engineer: FeatureEngineer) -> None:
        patient = {
            "age": 58,
            "gender": "M",
            "chronic_conditions": ["diabetes", "hipertension"],
            "active_medications": ["Metformina", "Losartan"],
            "visit_frequency_6m": 4,
            "recent_lab_values": {
                "glucosa": 126.0, "hemoglobina": 14.2,
                "colesterol": 245.0, "trigliceridos": 180.0,
                "creatinina": 0.9, "presion_sistolica": 130.0,
                "presion_diastolica": 85.0,
            },
            "alert_count": 2,
            "days_since_last_visit": 30,
        }
        result = engineer.extract_patient_features(patient)
        assert isinstance(result, np.ndarray)
        assert len(result) == 14

    def test_gender_encoding(self, engineer: FeatureEngineer) -> None:
        male = engineer.extract_patient_features({"gender": "M"})
        female = engineer.extract_patient_features({"gender": "F"})
        assert male[1] == 0.0
        assert female[1] == 1.0

    def test_missing_fields_default_zero(self, engineer: FeatureEngineer) -> None:
        result = engineer.extract_patient_features({})
        assert result[0] == 0.0  # age
        assert len(result) == 14

    def test_batch_extraction(self, engineer: FeatureEngineer) -> None:
        patients = [
            {"age": 45, "gender": "F", "chronic_conditions": ["diabetes"]},
            {"age": 62, "gender": "M", "chronic_conditions": ["hipertension", "diabetes"]},
        ]
        features, names = engineer.extract_patient_features_batch(patients)
        assert features.shape == (2, 14)
        assert len(names) == 14


class TestExtractLabFeatures:
    def test_normal_values(self, engineer: FeatureEngineer) -> None:
        lab_results = [
            {"value": 90, "range_min": 70, "range_max": 100},
            {"value": 14, "range_min": 12, "range_max": 16},
        ]
        result = engineer.extract_lab_features(lab_results)
        assert isinstance(result, np.ndarray)
        # 2 features per result + 2 summary features
        assert len(result) == 6

    def test_out_of_range_detected(self, engineer: FeatureEngineer) -> None:
        lab_results = [
            {"value": 200, "range_min": 70, "range_max": 100},  # high
        ]
        result = engineer.extract_lab_features(lab_results)
        # Last feature is ratio of out-of-range
        assert result[-1] == 1.0

    def test_empty_results(self, engineer: FeatureEngineer) -> None:
        result = engineer.extract_lab_features([])
        assert len(result) == 3
        assert np.all(result == 0)


class TestNormalizeFeatures:
    def test_standardizes(self, engineer: FeatureEngineer) -> None:
        data = np.array([[1, 2], [3, 4], [5, 6]], dtype=np.float64)
        normalized = engineer.normalize_features(data, fit=True)
        assert normalized.shape == data.shape
        # Mean should be ~0 after standardization
        assert abs(np.mean(normalized)) < 0.1
