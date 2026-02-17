"""
Clustering no supervisado de pacientes por perfil de riesgo.

Agrupa pacientes similares para identificar poblaciones en riesgo
usando K-Means y DBSCAN con visualizacion PCA.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from app.utils.logger import get_logger

logger = get_logger(__name__)

RISK_LEVELS: dict[int, str] = {
    0: "bajo",
    1: "medio",
    2: "alto",
    3: "critico",
}


@dataclass
class ClusterDescription:
    """Descripcion interpretable de un cluster."""

    cluster_id: int
    size: int
    risk_level: str
    centroid: list[float] = field(default_factory=list)
    top_features: list[tuple[str, float]] = field(default_factory=list)
    description: str = ""


@dataclass
class ClusteringResult:
    """Resultado completo de clustering."""

    labels: list[int] = field(default_factory=list)
    n_clusters: int = 0
    silhouette: float = 0.0
    descriptions: list[ClusterDescription] = field(default_factory=list)
    method: str = ""


class RiskClusterer:
    """Clustering de pacientes por perfil de riesgo."""

    def __init__(self) -> None:
        """Inicializa el clusterer."""
        self._kmeans: Optional[KMeans] = None
        self._dbscan: Optional[DBSCAN] = None
        self._scaler: StandardScaler = StandardScaler()
        self._pca: Optional[PCA] = None
        self._is_fitted = False
        self._feature_names: list[str] = []

    def find_optimal_clusters(
        self, features: np.ndarray, max_k: int = 10
    ) -> int:
        """Encuentra K optimo usando metodo del codo y silhouette.

        Args:
            features: Matriz de features (n_samples, n_features).
            max_k: Maximo K a evaluar.

        Returns:
            K optimo seleccionado.
        """
        n_samples = features.shape[0]
        max_k = min(max_k, n_samples - 1)
        if max_k < 2:
            return 2

        scaled = self._scaler.fit_transform(features)

        silhouette_scores: list[float] = []
        inertias: list[float] = []

        for k in range(2, max_k + 1):
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = km.fit_predict(scaled)
            inertias.append(km.inertia_)

            if len(set(labels)) > 1:
                sil = silhouette_score(scaled, labels)
            else:
                sil = -1.0
            silhouette_scores.append(sil)

        best_k_sil = int(np.argmax(silhouette_scores)) + 2

        # Elbow method: find point of maximum curvature
        if len(inertias) >= 3:
            diffs = np.diff(inertias)
            diffs2 = np.diff(diffs)
            best_k_elbow = int(np.argmax(np.abs(diffs2))) + 2
        else:
            best_k_elbow = best_k_sil

        # Prefer silhouette selection, but constrain
        optimal_k = best_k_sil

        logger.info(
            "optimal_k_found",
            k_silhouette=best_k_sil,
            k_elbow=best_k_elbow,
            selected=optimal_k,
            best_silhouette=max(silhouette_scores) if silhouette_scores else 0,
        )

        return optimal_k

    def fit_kmeans(
        self,
        features: np.ndarray,
        n_clusters: Optional[int] = None,
        feature_names: Optional[list[str]] = None,
    ) -> ClusteringResult:
        """Ajusta K-Means clustering.

        Args:
            features: Matriz de features.
            n_clusters: Numero de clusters. Si None, usa find_optimal_clusters.
            feature_names: Nombres de las features.

        Returns:
            ClusteringResult con labels, metricas y descripciones.
        """
        if feature_names:
            self._feature_names = feature_names

        scaled = self._scaler.fit_transform(features)

        if n_clusters is None:
            n_clusters = self.find_optimal_clusters(features)

        self._kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10,
            max_iter=300,
        )
        labels = self._kmeans.fit_predict(scaled)

        sil = 0.0
        if len(set(labels)) > 1:
            sil = float(silhouette_score(scaled, labels))

        descriptions = self._describe_clusters(
            features, scaled, labels, self._kmeans.cluster_centers_
        )

        self._is_fitted = True

        logger.info(
            "kmeans_fitted",
            n_clusters=n_clusters,
            silhouette=f"{sil:.4f}",
        )

        return ClusteringResult(
            labels=labels.tolist(),
            n_clusters=n_clusters,
            silhouette=sil,
            descriptions=descriptions,
            method="kmeans",
        )

    def fit_dbscan(
        self,
        features: np.ndarray,
        eps: float = 0.5,
        min_samples: int = 5,
        feature_names: Optional[list[str]] = None,
    ) -> ClusteringResult:
        """Ajusta DBSCAN clustering.

        Identifica clusters de forma natural y outliers (label=-1)
        como casos especiales de riesgo.

        Args:
            features: Matriz de features.
            eps: Radio maximo de vecindad.
            min_samples: Minimo de muestras para core point.
            feature_names: Nombres de las features.

        Returns:
            ClusteringResult con labels y metricas.
        """
        if feature_names:
            self._feature_names = feature_names

        scaled = self._scaler.fit_transform(features)

        self._dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = self._dbscan.fit_predict(scaled)

        unique_labels = set(labels)
        n_clusters = len(unique_labels - {-1})
        n_outliers = int(np.sum(labels == -1))

        sil = 0.0
        if n_clusters > 1:
            non_outlier = labels != -1
            if np.sum(non_outlier) > 1:
                sil = float(silhouette_score(scaled[non_outlier], labels[non_outlier]))

        descriptions = self._describe_clusters_dbscan(features, scaled, labels)

        self._is_fitted = True

        logger.info(
            "dbscan_fitted",
            n_clusters=n_clusters,
            n_outliers=n_outliers,
            silhouette=f"{sil:.4f}",
        )

        return ClusteringResult(
            labels=labels.tolist(),
            n_clusters=n_clusters,
            silhouette=sil,
            descriptions=descriptions,
            method="dbscan",
        )

    def predict_cluster(self, features: np.ndarray) -> list[int]:
        """Predice cluster para nuevos datos usando K-Means.

        Args:
            features: Matriz de features nuevas.

        Returns:
            Lista de labels de cluster.
        """
        if self._kmeans is None:
            raise RuntimeError("K-Means not fitted. Call fit_kmeans() first.")
        scaled = self._scaler.transform(features)
        return self._kmeans.predict(scaled).tolist()

    def visualize_clusters(
        self,
        features: np.ndarray,
        labels: np.ndarray,
        output_path: Optional[str] = None,
    ) -> str:
        """Genera visualizacion PCA 2D de clusters.

        Args:
            features: Matriz de features.
            labels: Labels de cluster.
            output_path: Ruta para guardar imagen. Si None, genera path.

        Returns:
            Path a la imagen PNG generada.
        """
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        scaled = self._scaler.transform(features) if self._is_fitted else features

        self._pca = PCA(n_components=2, random_state=42)
        pca_result = self._pca.fit_transform(scaled)

        if output_path is None:
            output_path = "cluster_visualization.png"

        fig, ax = plt.subplots(1, 1, figsize=(10, 8))

        unique_labels = sorted(set(labels))
        colors = plt.cm.Set2(np.linspace(0, 1, len(unique_labels)))

        for i, label in enumerate(unique_labels):
            mask = np.array(labels) == label
            name = f"Cluster {label}" if label >= 0 else "Outliers"
            marker = "x" if label == -1 else "o"
            ax.scatter(
                pca_result[mask, 0], pca_result[mask, 1],
                c=[colors[i]], label=name, marker=marker,
                alpha=0.7, s=60, edgecolors="k", linewidth=0.5,
            )

        ax.set_xlabel(f"PC1 ({self._pca.explained_variance_ratio_[0]:.1%})")
        ax.set_ylabel(f"PC2 ({self._pca.explained_variance_ratio_[1]:.1%})")
        ax.set_title("Clustering de Pacientes por Perfil de Riesgo")
        ax.legend()
        ax.grid(True, alpha=0.3)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        logger.info("cluster_visualization_saved", path=output_path)
        return output_path

    def save(self, path: str) -> None:
        """Guarda modelos de clustering.

        Args:
            path: Directorio de salida.
        """
        save_dir = Path(path)
        save_dir.mkdir(parents=True, exist_ok=True)

        joblib.dump(self._scaler, save_dir / "scaler.joblib")
        if self._kmeans:
            joblib.dump(self._kmeans, save_dir / "kmeans.joblib")
        if self._dbscan:
            joblib.dump(self._dbscan, save_dir / "dbscan.joblib")
        if self._pca:
            joblib.dump(self._pca, save_dir / "pca.joblib")

        metadata = {
            "is_fitted": self._is_fitted,
            "feature_names": self._feature_names,
        }
        joblib.dump(metadata, save_dir / "metadata.joblib")
        logger.info("clusterer_saved", path=path)

    def load(self, path: str) -> None:
        """Carga modelos de clustering.

        Args:
            path: Directorio con los modelos.
        """
        load_dir = Path(path)
        self._scaler = joblib.load(load_dir / "scaler.joblib")

        kmeans_path = load_dir / "kmeans.joblib"
        if kmeans_path.exists():
            self._kmeans = joblib.load(kmeans_path)

        dbscan_path = load_dir / "dbscan.joblib"
        if dbscan_path.exists():
            self._dbscan = joblib.load(dbscan_path)

        pca_path = load_dir / "pca.joblib"
        if pca_path.exists():
            self._pca = joblib.load(pca_path)

        meta_path = load_dir / "metadata.joblib"
        if meta_path.exists():
            metadata = joblib.load(meta_path)
            self._is_fitted = metadata.get("is_fitted", True)
            self._feature_names = metadata.get("feature_names", [])

        logger.info("clusterer_loaded", path=path)

    def _describe_clusters(
        self,
        raw_features: np.ndarray,
        scaled_features: np.ndarray,
        labels: np.ndarray,
        centroids: np.ndarray,
    ) -> list[ClusterDescription]:
        """Genera descripciones interpretables para K-Means clusters."""
        descriptions: list[ClusterDescription] = []
        n_clusters = len(centroids)

        centroid_norms = np.linalg.norm(centroids, axis=1)
        risk_order = np.argsort(centroid_norms)
        risk_map: dict[int, str] = {}
        n_levels = len(RISK_LEVELS)
        for rank, cluster_id in enumerate(risk_order):
            level_idx = min(int(rank * n_levels / n_clusters), n_levels - 1)
            risk_map[int(cluster_id)] = RISK_LEVELS[level_idx]

        for cluster_id in range(n_clusters):
            mask = labels == cluster_id
            cluster_raw = raw_features[mask]
            size = int(np.sum(mask))

            centroid_raw = np.mean(cluster_raw, axis=0) if size > 0 else centroids[cluster_id]

            top_features: list[tuple[str, float]] = []
            if self._feature_names:
                feature_importance = np.abs(centroids[cluster_id])
                top_idx = np.argsort(feature_importance)[::-1][:5]
                for idx in top_idx:
                    if idx < len(self._feature_names):
                        top_features.append((
                            self._feature_names[idx],
                            float(centroid_raw[idx]) if idx < len(centroid_raw) else 0.0,
                        ))

            descriptions.append(ClusterDescription(
                cluster_id=cluster_id,
                size=size,
                risk_level=risk_map.get(cluster_id, "medio"),
                centroid=centroid_raw.tolist() if hasattr(centroid_raw, "tolist") else [],
                top_features=top_features,
            ))

        return descriptions

    def _describe_clusters_dbscan(
        self,
        raw_features: np.ndarray,
        scaled_features: np.ndarray,
        labels: np.ndarray,
    ) -> list[ClusterDescription]:
        """Genera descripciones para DBSCAN clusters."""
        descriptions: list[ClusterDescription] = []
        unique_labels = sorted(set(labels))

        for label in unique_labels:
            mask = labels == label
            cluster_raw = raw_features[mask]
            size = int(np.sum(mask))
            centroid = np.mean(cluster_raw, axis=0)

            if label == -1:
                risk_level = "critico"
            else:
                risk_level = RISK_LEVELS.get(min(label, 3), "medio")

            top_features: list[tuple[str, float]] = []
            if self._feature_names:
                feature_vals = np.mean(np.abs(cluster_raw), axis=0)
                top_idx = np.argsort(feature_vals)[::-1][:5]
                for idx in top_idx:
                    if idx < len(self._feature_names):
                        top_features.append((
                            self._feature_names[idx],
                            float(centroid[idx]),
                        ))

            descriptions.append(ClusterDescription(
                cluster_id=int(label),
                size=size,
                risk_level=risk_level,
                centroid=centroid.tolist(),
                top_features=top_features,
                description="Outliers (riesgo especial)" if label == -1 else "",
            ))

        return descriptions
