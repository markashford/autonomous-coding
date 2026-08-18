from pathlib import Path

from settings import _int_from_env, load_settings, resolve_project_dir


def test_int_from_env_falls_back_on_invalid(monkeypatch):
    monkeypatch.setenv("AUTONOMOUS_MAX_TURNS", "not-a-number")
    assert _int_from_env("AUTONOMOUS_MAX_TURNS", 1000) == 1000


def test_int_from_env_rejects_values_below_minimum(monkeypatch):
    monkeypatch.setenv("AUTONOMOUS_MAX_TURNS", "0")
    assert _int_from_env("AUTONOMOUS_MAX_TURNS", 1000) == 1000


def test_load_settings_reads_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("AUTONOMOUS_DEFAULT_MODEL", "claude-test-model")
    monkeypatch.setenv("AUTONOMOUS_AUTO_CONTINUE_DELAY_SECONDS", "7")
    monkeypatch.setenv("AUTONOMOUS_GENERATIONS_DIR", str(tmp_path))
    settings = load_settings()
    assert settings.default_model == "claude-test-model"
    assert settings.auto_continue_delay_seconds == 7
    assert settings.generations_root == tmp_path


def test_resolve_project_dir_nests_relative_paths(tmp_path):
    resolved = resolve_project_dir(Path("demo_app"), tmp_path)
    assert resolved == tmp_path / "demo_app"


def test_resolve_project_dir_keeps_absolute_paths(tmp_path):
    absolute = tmp_path / "outside"
    assert resolve_project_dir(absolute, tmp_path / "generations") == absolute
