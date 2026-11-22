"""Парсер файла тестового репозитория (пакеты — заглавные латинские)."""

from typing import Dict, List

from .errors import DataError

VALID_NAME = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def _validate_name(name: str) -> str:
    """Проверить, что имя пакета — заглавные латинские буквы."""
    if not name or any(ch not in VALID_NAME for ch in name):
        raise DataError(
            f"Некорректное имя пакета {name!r}: "
            "ожидаются заглавные латинские буквы"
        )
    return name


def parse_test_repo(path: str) -> Dict[str, List[str]]:
    """Прочитать файл тестового репозитория в словарь зависимостей."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            lines = handle.readlines()
    except OSError as exc:
        raise DataError(f"Не удалось прочитать {path}: {exc}") from exc

    graph: Dict[str, List[str]] = {}
    for raw in lines:
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            raise DataError(f"Некорректная строка: {raw.rstrip()!r}")
        name, deps_raw = line.split(":", 1)
        name = _validate_name(name.strip())
        deps = [
            _validate_name(d.strip())
            for d in deps_raw.split(",")
            if d.strip()
        ]
        graph[name] = deps
    return graph