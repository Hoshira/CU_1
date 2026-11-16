"""Тесты разбора и валидации конфигурации."""

import os

import pytest

from src.pkgviz.config import AppConfig, parse_config
from src.pkgviz.errors import ConfigError


def _valid_argv(tmp_path):
    local_dir = tmp_path / "repo"
    local_dir.mkdir()
    return [
        "--package", "requests",
        "--repo", str(local_dir),
        "--mode", "local",
        "--version", "2.31.0",
    ]


def test_parse_config_local(tmp_path):
    cfg = parse_config(_valid_argv(tmp_path))
    assert isinstance(cfg, AppConfig)
    assert cfg.package == "requests"
    assert cfg.mode == "local"
    assert cfg.version == "2.31.0"
    assert os.path.isdir(cfg.repo)


def test_parse_config_remote():
    argv = [
        "--package", "requests",
        "--repo", "https://github.com/psf/requests",
        "--mode", "remote",
        "--version", "2.31.0",
    ]
    cfg = parse_config(argv)
    assert cfg.mode == "remote"


def test_invalid_package_name(tmp_path):
    argv = _valid_argv(tmp_path)
    argv[1] = "bad name!"
    with pytest.raises(ConfigError):
        parse_config(argv)


def test_invalid_mode(tmp_path):
    argv = _valid_argv(tmp_path)
    argv[5] = "cloud"
    with pytest.raises(SystemExit):
        # argparse обрабатывает choices через SystemExit
        parse_config(argv)


def test_invalid_local_repo(tmp_path):
    argv = _valid_argv(tmp_path)
    argv[3] = str(tmp_path / "does-not-exist")
    with pytest.raises(ConfigError):
        parse_config(argv)


def test_invalid_remote_repo():
    argv = [
        "--package", "requests",
        "--repo", "ftp://example.com/repo",
        "--mode", "remote",
        "--version", "2.31.0",
    ]
    with pytest.raises(ConfigError):
        parse_config(argv)


def test_invalid_version(tmp_path):
    argv = _valid_argv(tmp_path)
    argv[7] = "1.0 beta"
    with pytest.raises(ConfigError):
        parse_config(argv)