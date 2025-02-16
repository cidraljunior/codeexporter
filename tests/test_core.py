import pytest
from pathlib import Path
import zipfile
from codeexporter.core import ProjectExporter, analyze_code_structure
from codeexporter.config import Config


@pytest.fixture
def sample_project(tmp_path):
    (tmp_path / "test.py").write_text("def foo():\n    pass\n")
    (tmp_path / "ignore.txt").touch()
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "file.md").touch()
    return tmp_path


@pytest.fixture
def default_config(sample_project):
    return Config(
        project_dir=sample_project, ignore_files=["ignore.txt"], ignore_ext=[".md"]
    )


def test_file_processing(sample_project, default_config):
    exporter = ProjectExporter(default_config)
    exporter.export(sample_project, Path("output.txt"), "text")

    assert exporter.stats["processed"] == 1  # Only test.py
    assert exporter.stats["skipped"] >= 2


def test_zip_output(sample_project, default_config):
    output_path = sample_project / "output.zip"
    exporter = ProjectExporter(default_config)
    exporter.export(sample_project, output_path, "zip")

    with zipfile.ZipFile(output_path) as z:
        assert "test.py" in z.namelist()
        assert "ignore.txt" not in z.namelist()


def test_ast_analysis():
    code = "class MyClass:\n    def method(self):\n        pass\n"
    analysis = analyze_code_structure(code)

    assert len(analysis["classes"]) == 1
    assert analysis["classes"][0]["name"] == "MyClass"
    assert len(analysis["functions"]) == 1
