"""CLI-интерфейс приложения (этап 5)."""

import os
import sys
from typing import Dict, List, Optional

from .config import AppConfig, parse_config
from .d2_render import graph_to_d2, reverse_graph_to_d2
from .errors import ConfigError, DataError, ExitCode
from .graph import (
    build_graph_dfs,
    collect_reverse_dependencies,
    find_cycles,
)
from .packages_parser import (
    extract_dependency_names,
    find_any_version,
    get_direct_dependencies,
    parse_packages,
)
from .repository import load_packages
from .test_repo_parser import parse_test_repo


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


def _get_deps_by_name(
    packages: List[Dict[str, str]],
    name: str,
) -> List[str]:
    """Вернуть прямые зависимости пакета по имени (без версии)."""
    pkg = find_any_version(packages, name)
    if pkg is None:
        return []
    deps: List[str] = []
    for field in ("Pre-Depends", "Depends"):
        deps.extend(extract_dependency_names(pkg.get(field, "")))
    return deps


def _resolve_real_graph(config: AppConfig) -> Dict[str, List[str]]:
    """Построить полный граф из реального репозитория по имени пакета."""
    text = (
        _load_local_packages(config.repo)
        if config.mode == "local"
        else _load_remote_packages(config)
    )
    packages = parse_packages(text)

    def get_deps(name: str) -> List[str]:
        return _get_deps_by_name(packages, name)

    return build_graph_dfs(config.package, get_deps)


def _resolve_test_graph(config: AppConfig) -> Dict[str, List[str]]:
    """Построить граф из файла тестового репозитория."""
    deps_map = parse_test_repo(config.test_repo)

    if config.reverse or config.d2:
        if config.package not in deps_map:
            raise DataError(
                f"Пакет {config.package} не описан "
                "в тестовом репозитории"
            )
        return deps_map

    def get_deps(name: str) -> List[str]:
        if name not in deps_map:
            raise DataError(
                f"Пакет {name} не описан в тестовом репозитории"
            )
        return deps_map[name]

    return build_graph_dfs(config.package, get_deps)


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


def _print_test_graph(graph: Dict[str, List[str]], root: str) -> None:
    """Вывести граф в читаемом виде и циклы, если есть."""
    print(f"Граф зависимостей от {root}:")
    for node in sorted(graph):
        deps = ", ".join(graph[node]) if graph[node] else "(нет)"
        print(f"  {node} -> {deps}")

    cycles = find_cycles(graph, root)
    if cycles:
        print("Обнаружены циклы:")
        for cycle in cycles:
            print("  " + " -> ".join(cycle))
    else:
        print("Циклов не обнаружено.")


def _print_reverse_dependencies(
    graph: Dict[str, List[str]],
    target: str,
) -> None:
    """Вывести пакеты, которые зависят от target (транзитивно)."""
    parents = collect_reverse_dependencies(graph, target)
    if not parents:
        print(f"Обратных зависимостей для {target} нет.")
        return
    print(f"Обратные зависимости для {target}:")
    for name in sorted(parents):
        print(f"  - {name}")


def _print_error(message: str) -> None:
    """Вывести сообщение об ошибке в stderr."""
    print(f"[ERROR] {message}", file=sys.stderr)


def main(argv: Optional[List[str]] = None) -> int:
    """Точка входа CLI: разбор параметров и вывод результата."""
    try:
        config = parse_config(argv)
    except ConfigError as exc:
        _print_error(str(exc))
        return ExitCode.CONFIG_ERROR

    try:
        if config.test_repo:
            graph = _resolve_test_graph(config)
            if config.reverse:
                if config.d2:
                    print(reverse_graph_to_d2(graph, config.package))
                else:
                    _print_reverse_dependencies(graph, config.package)
            else:
                if config.d2:
                    print(graph_to_d2(graph))
                else:
                    _print_test_graph(graph, config.package)
        else:
            if config.d2:
                graph = _resolve_real_graph(config)
                print(graph_to_d2(graph))
            else:
                deps = _resolve_dependencies(config)
                _print_dependencies(config, deps)
    except DataError as exc:
        _print_error(str(exc))
        return ExitCode.DATA_ERROR
    except LookupError as exc:
        _print_error(str(exc))
        return ExitCode.DATA_ERROR

    return ExitCode.OK


if __name__ == "__main__":
    sys.exit(main())