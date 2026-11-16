"""Интеграционные тесты точки входа `python -m src.pkgviz`."""

import subprocess
import sys


def _run_module(*args):
    """Запустить `python -m src.pkgviz` и вернуть CompletedProcess."""
    return subprocess.run(
        [sys.executable, "-m", "src.pkgviz", *args],
        capture_output=True,
        text=True,
    )


def test_entrypoint_returns_zero_on_success(tmp_path):
    """Успешный запуск: код 0 и вывод зависимостей."""
    local_dir = tmp_path / "repo"
    local_dir.mkdir()
    (local_dir / "Packages").write_text(
        "Package: requests\n"
        "Version: 2.31.0\n"
        "Depends: urllib3\n",
        encoding="utf-8",
    )
    result = _run_module(
        "--package", "requests",
        "--repo", str(local_dir),
        "--mode", "local",
        "--version", "2.31.0",
    )
    assert result.returncode == 0
    assert "Прямые зависимости пакета requests" in result.stdout
    assert "- urllib3" in result.stdout


def test_entrypoint_returns_two_on_config_error():
    """Ошибка конфигурации: код 2 и сообщение в stderr."""
    result = _run_module(
        "--package", "bad name!",
        "--repo", "https://github.com/psf/requests",
        "--mode", "remote",
        "--version", "2.31.0",
    )
    assert result.returncode == 2
    assert "[ERROR]" in result.stderr


def test_entrypoint_returns_three_when_package_missing(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "Packages").write_text(
        "Package: bash\nVersion: 5.1\n",
        encoding="utf-8",
    )
    result = _run_module(
        "--package", "bash",
        "--repo", str(repo),
        "--mode", "local",
        "--version", "9.9",
    )
    assert result.returncode == 3
    assert "[ERROR]" in result.stderr