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
    """Успешный запуск: код 0 и вывод всех параметров."""
    local_dir = tmp_path / "repo"
    local_dir.mkdir()
    result = _run_module(
        "--package", "requests",
        "--repo", str(local_dir),
        "--mode", "local",
        "--version", "2.31.0",
    )
    assert result.returncode == 0
    assert "package: requests" in result.stdout
    assert "mode: local" in result.stdout


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