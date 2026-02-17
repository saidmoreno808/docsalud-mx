"""
Tests unitarios para RiskClusterer.
"""

import numpy as np
import pytest

from app.core.ml.risk_clusterer import (
    ClusterDescription,
    ClusteringResult,
    RiskClusterer,
)


@pytest.fixture
def patient_features() -> np.ndarray:
    """Features sinteticas de 60 pacientes con 3 clusters."""
    rng = np.random.RandomState(42)
    cluster1 = rng.normal(loc=[30, 0, 0, 0, 90], scale=5, size=(20, 5))
    cluster2 = rng.normal(loc=[55, 1, 2, 3, 130], scale=5, size=(20, 5))
    cluster3 = rng.normal(loc=[70, 1, 4, 5, 180], scale=5, size=(20, 5))
    return np.vstack([cluster1, cluster2, cluster3])


@pytest.fixture
def feature_names() -> list[str]:
    return ["age", "gender", "n_chronic", "n_medications", "glucosa"]


class TestFindOptimalClusters:
    def test_finds_reasonable_k(self, patient_features: np.ndarray) -> None:
        clusterer = RiskClusterer()
        k = clusterer.find_optimal_clusters(patient_features, max_k=8)
        assert 2 <= k <= 8

    def test_small_dataset(self) -> None:
        data = np.array([[1, 2], [3, 4], [5, 6]])
        clusterer = RiskClusterer()
        k = clusterer.find_optimal_clusters(data, max_k=5)
        assert k == 2


class TestFitKMeans:
    def test_returns_clustering_result(self, patient_features: np.ndarray) -> None:
        clusterer = RiskClusterer()
        result = clusterer.fit_kmeans(patient_features, n_clusters=3)
        assert isinstance(result, ClusteringResult)
        assert result.method == "kmeans"

    def test_assigns_all_labels(self, patient_features: np.ndarray) -> None:
        clusterer = RiskClusterer()
        result = clusterer.fit_kmeans(patient_features, n_clusters=3)
        assert len(result.labels) == len(patient_features)

    def test_correct_n_clusters(self, patient_features: np.ndarray) -> None:
        clusterer = RiskClusterer()
        result = clusterer.fit_kmeans(patient_features, n_clusters=3)
        assert result.n_clusters == 3

    def test_positive_silhouette(self, patient_features: np.ndarray) -> None:
        clusterer = RiskClusterer()
        result = clusterer.fit_kmeans(patient_features, n_clusters=3)
        assert result.silhouette > 0

    def test_generates_descriptions(
        self, patient_features: np.ndarray, feature_names: list[str]
    ) -> None:
        clusterer = RiskClusterer()
        result = clusterer.fit_kmeans(
            patient_features, n_clusters=3, feature_names=feature_names
        )
        assert len(result.descriptions) == 3
        for desc in result.descriptions:
            assert isinstance(desc, ClusterDescription)
            assert desc.size > 0
            assert desc.risk_level in ["bajo", "medio", "alto", "critico"]

    def test_auto_selects_k(self, patient_features: np.ndarray) -> None:
        clusterer = RiskClusterer()
        result = clusterer.fit_kmeans(patient_features)
        assert result.n_clusters >= 2


class TestFitDBSCAN:
    def test_returns_result(self, patient_features: np.ndarray) -> None:
        clusterer = RiskClusterer()
        result = clusterer.fit_dbscan(patient_features, eps=2.0, min_samples=3)
        assert isinstance(result, ClusteringResult)
        assert result.method == "dbscan"

    def test_assigns_labels(self, patient_features: np.ndarray) -> None:
        clusterer = RiskClusterer()
        result = clusterer.fit_dbscan(patient_features, eps=2.0, min_samples=3)
        assert len(result.labels) == len(patient_features)

    def test_finds_outliers_with_tight_eps(self, patient_features: np.ndarray) -> None:
        clusterer = RiskClusterer()
        result = clusterer.fit_dbscan(patient_features, eps=0.1, min_samples=3)
        assert -1 in result.labels  # Should have outliers with very tight eps

    def test_outliers_marked_critical(self, patient_features: np.ndarray) -> None:
        clusterer = RiskClusterer()
        result = clusterer.fit_dbscan(patient_features, eps=0.1, min_samples=3)
        outlier_descs = [d for d in result.descriptions if d.cluster_id == -1]
        if outlier_descs:
            assert outlier_descs[0].risk_level == "critico"


class TestPredictCluster:
    def test_predicts_new_data(self, patient_features: np.ndarray) -> None:
        clusterer = RiskClusterer()
        clusterer.fit_kmeans(patient_features, n_clusters=3)
        new_data = np.array([[55, 1, 2, 3, 130]])
        preds = clusterer.predict_cluster(new_data)
        assert len(preds) == 1
        assert preds[0] in [0, 1, 2]

    def test_unfitted_raises(self) -> None:
        clusterer = RiskClusterer()
        with pytest.raises(RuntimeError):
            clusterer.predict_cluster(np.array([[1, 2, 3, 4, 5]]))


class TestVisualize:
    def test_creates_image(self, patient_features: np.ndarray, tmp_path: str) -> None:
        clusterer = RiskClusterer()
        result = clusterer.fit_kmeans(patient_features, n_clusters=3)
        output = str(tmp_path) + "/clusters.png"
        path = clusterer.visualize_clusters(
            patient_features, np.array(result.labels), output_path=output
        )
        from pathlib import Path
        assert Path(path).exists()


class TestSaveLoad:
    def test_save_load_preserves(
        self, patient_features: np.ndarray, tmp_path: str
    ) -> None:
        clusterer = RiskClusterer()
        clusterer.fit_kmeans(patient_features, n_clusters=3)
        original_preds = clusterer.predict_cluster(patient_features[:5])

        save_path = str(tmp_path) + "/clusterer"
        clusterer.save(save_path)

        loaded = RiskClusterer()
        loaded.load(save_path)
        restored_preds = loaded.predict_cluster(patient_features[:5])

        assert original_preds == restored_preds
