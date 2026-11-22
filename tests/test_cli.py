"""Тесты CLI-интерфейса этапа 1."""

import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
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


def test_main_prints_reverse_dependencies(tmp_path, capsys):
    fixture = Path("tests/fixtures/test_graph_reverse.txt")
    argv = [
        "--package", "D",
        "--repo", "dummy",
        "--mode", "local",
        "--version", "1.0",
        "--test-repo", str(fixture),
        "--reverse",
    ]
    rc = main(argv)
    out = capsys.readouterr().out
    assert rc == 0
    assert "Обратные зависимости для D" in out
    assert "A" in out
    assert "B" in out
    assert "C" in out


def test_main_prints_d2_in_test_mode(capsys):
    argv = [
        "--package", "A",
        "--repo", "dummy",
        "--mode", "local",
        "--version", "1.0",
        "--test-repo", "tests/fixtures/test_graph_simple.txt",
        "--d2",
    ]
    rc = main(argv)
    out = capsys.readouterr().out
    assert rc == 0
    assert "direction: down" in out
    assert "A -> B" in out
    assert "A -> C" in out


def test_main_prints_reverse_d2(capsys):
    argv = [
        "--package", "D",
        "--repo", "dummy",
        "--mode", "local",
        "--version", "1.0",
        "--test-repo", "tests/fixtures/test_graph_reverse.txt",
        "--reverse",
        "--d2",
    ]
    rc = main(argv)
    out = capsys.readouterr().out
    assert rc == 0
    assert "direction: down" in out
    assert "B -> D" in out
    assert "C -> D" in out