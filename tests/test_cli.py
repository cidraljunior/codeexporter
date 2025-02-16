import pytest
from click.testing import CliRunner
from pathlib import Path
from codeexporter.cli import main


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_basic_command(runner, tmp_path):
    result = runner.invoke(main, [str(tmp_path), "-o", "output.txt"])
    assert result.exit_code == 0
    assert Path("output.txt").exists()


def test_cli_output_formats(runner, tmp_path):
    # Test zip format
    result = runner.invoke(main, [str(tmp_path), "--format", "zip", "-o", "output.zip"])
    assert result.exit_code == 0
    assert Path("output.zip").is_file()


def test_cli_invalid_directory(runner):
    result = runner.invoke(main, ["/invalid/path"])
    assert result.exit_code != 0
    assert "does not exist" in result.output


def test_cli_config_override(runner, tmp_path):
    result = runner.invoke(
        main, [str(tmp_path), "--ignore-dirs", "tests", "--max-size", "2", "-v"]
    )
    assert result.exit_code == 0
    assert "processed" in result.output
