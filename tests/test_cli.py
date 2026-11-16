"""Тесты CLI-интерфейса этапа 1."""

import io
from contextlib import redirect_stderr, redirect_stdout

from src.pkgviz.cli import main
from src.pkgviz.errors import ExitCode


def test_main_prints_all_params(tmp_path, capsys):
    local_dir = tmp_path / "repo"
    local_dir.mkdir()
    argv = [
        "--package", "requests",
        "--repo", str(local_dir),
        "--mode", "local",
        "--version", "2.31.0",
    ]
    rc = main(argv)
    out = capsys.readouterr().out
    assert rc == ExitCode.OK
    assert "package: requests" in out
    assert f"repo: {local_dir}" in out
    assert "mode: local" in out
    assert "version: 2.31.0" in out


def test_main_returns_config_error_for_bad_package(tmp_path, capsys):
    argv = [
        "--package", "bad name!",
        "--repo", str(tmp_path),
        "--mode", "local",
        "--version", "1.0",
    ]
    rc = main(argv)
    err = capsys.readouterr().err
    assert rc == ExitCode.CONFIG_ERROR
    assert "[ERROR]" in err