"""
Tests unitarios para ModelRegistry.
"""

import json
from pathlib import Path

import pytest

from app.core.ml.model_registry import ModelInfo, ModelRegistry


@pytest.fixture
def registry(tmp_path: Path) -> ModelRegistry:
    return ModelRegistry(base_path=str(tmp_path))


@pytest.fixture
def registry_with_models(tmp_path: Path) -> ModelRegistry:
    """Registry con modelos registrados y archivos dummy."""
    reg = ModelRegistry(base_path=str(tmp_path))

    # Create dummy model files
    (tmp_path / "clf_v1.joblib").write_text("dummy")
    (tmp_path / "clf_v2.joblib").write_text("dummy")
    (tmp_path / "ner_v1").mkdir()

    reg.register("classifier", "1.0.0", "joblib", str(tmp_path / "clf_v1.joblib"),
                 metrics={"f1": 0.85})
    reg.register("classifier", "1.1.0", "joblib", str(tmp_path / "clf_v2.joblib"),
                 metrics={"f1": 0.90})
    reg.register("ner", "1.0.0", "spacy", str(tmp_path / "ner_v1"),
                 metrics={"f1": 0.78})
    return reg


class TestRegister:
    def test_registers_model(self, registry: ModelRegistry) -> None:
        info = registry.register("test_model", "1.0.0", "sklearn", "/path/model.joblib")
        assert isinstance(info, ModelInfo)
        assert info.name == "test_model"
        assert info.version == "1.0.0"

    def test_persists_to_disk(self, registry: ModelRegistry) -> None:
        registry.register("model", "1.0.0", "sklearn", "/path")
        reg_file = Path(registry.base_path) / "registry.json"
        assert reg_file.exists()
        data = json.loads(reg_file.read_text())
        assert "model:1.0.0" in data

    def test_stores_metrics(self, registry: ModelRegistry) -> None:
        info = registry.register(
            "model", "1.0.0", "sklearn", "/path", metrics={"f1": 0.92}
        )
        assert info.metrics["f1"] == 0.92


class TestListModels:
    def test_lists_all(self, registry_with_models: ModelRegistry) -> None:
        models = registry_with_models.list_models()
        assert len(models) == 3

    def test_empty_registry(self, registry: ModelRegistry) -> None:
        assert registry.list_models() == []


class TestListVersions:
    def test_lists_versions(self, registry_with_models: ModelRegistry) -> None:
        versions = registry_with_models.list_versions("classifier")
        assert versions == ["1.0.0", "1.1.0"]

    def test_no_versions(self, registry_with_models: ModelRegistry) -> None:
        versions = registry_with_models.list_versions("nonexistent")
        assert versions == []


class TestGetInfo:
    def test_gets_specific_version(self, registry_with_models: ModelRegistry) -> None:
        info = registry_with_models.get_info("classifier", "1.0.0")
        assert info.metrics["f1"] == 0.85

    def test_gets_latest(self, registry_with_models: ModelRegistry) -> None:
        info = registry_with_models.get_info("classifier")
        assert info.version == "1.1.0"

    def test_not_found_raises(self, registry_with_models: ModelRegistry) -> None:
        with pytest.raises(KeyError):
            registry_with_models.get_info("nonexistent")


class TestUnloadModel:
    def test_unloads(self, registry_with_models: ModelRegistry) -> None:
        # Manually add to loaded
        registry_with_models._loaded_models["classifier:1.0.0"] = "dummy"
        registry_with_models.unload_model("classifier", "1.0.0")
        assert "classifier:1.0.0" not in registry_with_models._loaded_models

    def test_unloads_all_versions(self, registry_with_models: ModelRegistry) -> None:
        registry_with_models._loaded_models["classifier:1.0.0"] = "dummy1"
        registry_with_models._loaded_models["classifier:1.1.0"] = "dummy2"
        registry_with_models.unload_model("classifier")
        assert len(registry_with_models._loaded_models) == 0


class TestPersistence:
    def test_loads_on_init(self, tmp_path: Path) -> None:
        reg1 = ModelRegistry(base_path=str(tmp_path))
        reg1.register("model", "1.0.0", "sklearn", "/path", metrics={"f1": 0.9})

        reg2 = ModelRegistry(base_path=str(tmp_path))
        info = reg2.get_info("model", "1.0.0")
        assert info.metrics["f1"] == 0.9
