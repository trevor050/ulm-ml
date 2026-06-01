from ulm_ml.paths import ARTIFACTS_DIR, DATA_DIR, MODELS_DIR, PROJECT_ROOT


def test_project_paths_are_rooted_in_repo() -> None:
    assert (PROJECT_ROOT / "pyproject.toml").exists()
    assert DATA_DIR == PROJECT_ROOT / "data"
    assert ARTIFACTS_DIR == PROJECT_ROOT / "artifacts"
    assert MODELS_DIR == PROJECT_ROOT / "models"
