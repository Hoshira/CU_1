"""Разбор и валидация параметров командной строки."""

import argparse
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import urlparse

from .errors import ConfigError

PACKAGE_NAME_RE = re.compile(r"^[A-Za-z0-9_.\-]{1,128}$")
VERSION_RE = re.compile(r"^[A-Za-z0-9_.\-+]{1,64}$")

VALID_MODES = ("local", "remote")


@dataclass(frozen=True)
class AppConfig:
    """Конфигурация приложения, собранная из аргументов CLI."""

    package: str
    repo: str
    mode: str
    version: str

    def as_dict(self) -> Dict[str, str]:
        """Представление конфигурации в виде словаря ключ-значение."""
        return {
            "package": self.package,
            "repo": self.repo,
            "mode": self.mode,
            "version": self.version,
        }


def build_parser() -> argparse.ArgumentParser:
    """Создать парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="pkgviz",
        description="Визуализация графа зависимостей пакета.",
    )
    parser.add_argument("-p", "--package", required=True, help="Имя пакета")
    parser.add_argument(
        "-r",
        "--repo",
        required=True,
        help="URL репозитория или путь к локальному каталогу",
    )
    parser.add_argument(
        "-m",
        "--mode",
        required=True,
        choices=VALID_MODES,
        help="Режим работы с репозиторием: local | remote",
    )
    parser.add_argument("-v", "--version", required=True, help="Версия пакета")
    return parser


def _validate_package(name: str) -> str:
    """Проверить имя пакета на допустимые символы."""
    if not PACKAGE_NAME_RE.match(name):
        raise ConfigError(
            f"Некорректное имя пакета {name!r}: "
            "разрешены только буквы, цифры, '.', '_' и '-' (1..128 символов)."
        )
    return name


def _validate_repo(repo: str, mode: str) -> str:
    """Проверить URL или локальный путь в зависимости от режима."""
    if mode == "local":
        if not os.path.isdir(repo):
            raise ConfigError(
                f"Локальный репозиторий не найден или не является каталогом: {repo!r}."
            )
        return repo

    parsed = urlparse(repo)
    if parsed.scheme not in ("http", "https"):
        raise ConfigError(
            f"Некорректный URL репозитория {repo!r}: "
            "ожидается http(s)-адрес."
        )
    if not parsed.netloc:
        raise ConfigError(f"В URL репозитория {repo!r} отсутствует хост.")
    return repo


def _validate_mode(mode: str) -> str:
    """Проверить режим работы (уже ограничен choices, но проверяем явно)."""
    if mode not in VALID_MODES:
        raise ConfigError(
            f"Некорректный режим {mode!r}. Допустимо: {', '.join(VALID_MODES)}."
        )
    return mode


def _validate_version(version: str) -> str:
    """Проверить строку версии."""
    if not VERSION_RE.match(version):
        raise ConfigError(
            f"Некорректная версия {version!r}: "
            "разрешены буквы, цифры, '.', '_', '-', '+' (1..64 символа)."
        )
    return version


def parse_config(argv: Optional[List[str]] = None) -> AppConfig:
    """Разобрать argv и вернуть валидную конфигурацию."""
    parser = build_parser()
    args = parser.parse_args(argv)

    mode = _validate_mode(args.mode)
    package = _validate_package(args.package)
    repo = _validate_repo(args.repo, mode)
    version = _validate_version(args.version)

    return AppConfig(package=package, repo=repo, mode=mode, version=version)