"""Тесты CLI-интерфейса этапа 1."""

import io
from contextlib import redirect_stderr, redirect_stdout

from src.pkgviz.cli import main
from src.pkgviz.errors import ExitCode


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


def test_main_prints_dependencies_from_local_repo(tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "Packages").write_text(
        "Package: bash\n"
        "Version: 5.1-6ubuntu1\n"
        "Depends: base-files (>= 2.1), libc6 (>= 2.34)\n",
        encoding="utf-8",
    )
    argv = [
        "--package", "bash",
        "--repo", str(repo),
        "--mode", "local",
        "--version", "5.1-6ubuntu1",
    ]
    rc = main(argv)
    out = capsys.readouterr().out
    assert rc == 0
    assert "Прямые зависимости пакета bash" in out
    assert "- base-files" in out
    assert "- libc6" in out


def test_main_returns_data_error_when_package_missing(tmp_path, capsys):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "Packages").write_text(
        "Package: bash\nVersion: 5.1\nDepends: libc6\n",
        encoding="utf-8",
    )
    argv = [
        "--package", "bash",
        "--repo", str(repo),
        "--mode", "local",
        "--version", "9.9",
    ]
    rc = main(argv)
    err = capsys.readouterr().err
    assert rc == 3
    assert "[ERROR]" in err
    assert "не найден" in err