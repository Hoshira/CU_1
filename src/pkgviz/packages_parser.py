"""Парсер файла Packages (формат deb822) и поля Depends."""

import re
from typing import Dict, List, Optional

# Регулярное выражение для удаления версии в скобках
_VERSION_IN_PARENS = re.compile(r"\(.*?\)")


def parse_packages(text: str) -> List[Dict[str, str]]:
    """Разобрать текст Packages в список словарей (по одному на пакет)."""
    packages: List[Dict[str, str]] = []
    for block in text.strip().split("\n\n"):
        if not block.strip():
            continue
        pkg: Dict[str, str] = {}
        current_key: Optional[str] = None
        for line in block.split("\n"):
            if not line.strip():
                continue
            if line.startswith((" ", "\t")) and current_key is not None:
                pkg[current_key] += "\n" + line.strip()
                continue
            if ": " in line:
                key, value = line.split(": ", 1)
                pkg[key] = value
                current_key = key
            else:
                current_key = None
        packages.append(pkg)
    return packages


def find_package(
    packages: List[Dict[str, str]],
    name: str,
    version: str,
) -> Optional[Dict[str, str]]:
    """Найти пакет по имени и точной версии."""
    for pkg in packages:
        if pkg.get("Package") == name and pkg.get("Version") == version:
            return pkg
    return None


def extract_dependency_names(depends_field: str) -> List[str]:
    """Извлечь имена прямых зависимостей из поля Depends.

    Отбрасывает версии в скобках и оставляет первую альтернативу
    из конструкций вида `a | b`.
    """
    if not depends_field:
        return []
    names: List[str] = []
    for part in depends_field.split(","):
        part = _VERSION_IN_PARENS.sub("", part).strip()
        part = part.split("|")[0].strip()
        if part:
            names.append(part)
    return names


def get_direct_dependencies(
    packages: List[Dict[str, str]],
    name: str,
    version: str,
) -> List[str]:
    """Вернуть имена прямых зависимостей пакета или пустой список.

    Учитывает и Depends, и Pre-Depends (оба — прямые зависимости).
    Бросает LookupError, если пакет заданной версии не найден.
    """
    pkg = find_package(packages, name, version)
    if pkg is None:
        raise LookupError(
            f"Пакет {name} версии {version} не найден в репозитории"
        )
    deps: List[str] = []
    for field in ("Pre-Depends", "Depends"):
        deps.extend(extract_dependency_names(pkg.get(field, "")))
    return deps