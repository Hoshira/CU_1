"""CLI-интерфейс приложения (этап 2)."""

import os
import sys
from typing import List, Optional

from .config import AppConfig, parse_config
from .errors import ConfigError, DataError, ExitCode
from .packages_parser import (
    get_direct_dependencies,
    parse_packages,
)
from .repository import fetch_packages_text, load_packages


def _load_local_packages(repo_path: str) -> str:
    """Прочитать локальный файл Packages из каталога."""
    candidate = os.path.join(repo_path, "Packages")
    if not os.path.isfile(candidate):
        raise DataError(
            f"В каталоге {repo_path} "
            "не найден файл Packages"
        )
    try:
        with open(candidate, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:
        raise DataError(
            f"Не удалось прочитать {candidate}: {exc}"
        ) from exc


def _load_remote_packages(config: AppConfig) -> str:
    """Скачать Packages.gz из удалённого репозитория."""
    return load_packages(
        config.repo,
        dist=config.dist,
        component=config.component,
        arch=config.arch,
    )


def _resolve_dependencies(config: AppConfig) -> List[str]:
    """Получить список прямых зависимостей для конфигурации."""
    if config.mode == "local":
        text = _load_local_packages(config.repo)
    else:
        text = _load_remote_packages(config)

    packages = parse_packages(text)
    return get_direct_dependencies(
        packages,
        config.package,
        config.version,
    )


def _print_dependencies(config: AppConfig, deps: List[str]) -> None:
    """Вывести прямые зависимости в требуемом формате."""
    header = (
        f"Прямые зависимости пакета {config.package} "
        f"({config.version}):"
    )
    print(header)
    if not deps:
        print("  (нет)")
        return
    for name in deps:
        print(f"  - {name}")


def _print_error(message: str) -> None:
    """Вывести сообщение об ошибке в stderr."""
    print(f"[ERROR] {message}", file=sys.stderr)


def main(argv: Optional[List[str]] = None) -> int:
    """Точка входа CLI: разбор параметров и вывод зависимостей."""
    try:
        config = parse_config(argv)
    except ConfigError as exc:
        _print_error(str(exc))
        return ExitCode.CONFIG_ERROR

    try:
        deps = _resolve_dependencies(config)
    except DataError as exc:
        _print_error(str(exc))
        return ExitCode.DATA_ERROR
    except LookupError as exc:
        _print_error(str(exc))
        return ExitCode.DATA_ERROR

    _print_dependencies(config, deps)
    return ExitCode.OK


if __name__ == "__main__":
    sys.exit(main())