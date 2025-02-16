import pytest
from pathlib import Path
import yaml
from codeexporter.config import load_configuration, Config


@pytest.fixture
def sample_project(tmp_path):
    (tmp_path / ".codeexportrc").write_text(
        yaml.dump({"ignore_dirs": ["build"], "max_size": 3})
    )
    return tmp_path


@pytest.fixture
def user_config(tmp_path):
    cfg_dir = tmp_path / ".config" / "codeexport"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "config.yaml").write_text(
        yaml.dump({"include_hidden": True, "ignore_files": [".DS_Store"]})
    )
    return tmp_path


def test_config_loading(sample_project):
    config = load_configuration(sample_project)
    assert "build" in config.ignore_dirs
    assert config.max_size == 3


def test_config_precedence(sample_project, user_config, monkeypatch):
    monkeypatch.setenv("HOME", str(user_config))

    config = load_configuration(
        sample_project, cli_args={"max_size": 5, "ignore_dirs": ("dist",)}
    )

    assert config.max_size == 5  # CLI should override
    assert "build" in config.ignore_dirs  # From project
    assert "dist" in config.ignore_dirs  # From CLI
    assert ".DS_Store" in config.ignore_files  # From user


def test_config_defaults():
    config = Config(project_dir=Path("."))
    assert config.use_gitignore is True
    assert config.include_hidden is False
