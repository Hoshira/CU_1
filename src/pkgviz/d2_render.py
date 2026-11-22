"""Генерация текстового представления графа на языке D2."""

from typing import Dict, List

from .graph import build_reverse_index


def _quote(name: str) -> str:
    """Обернуть имя пакета в кавычки, если есть спецсимволы."""
    safe = all(ch.isalnum() or ch in "_-." for ch in name)
    return name if safe else f'"{name}"'


def graph_to_d2(graph: Dict[str, List[str]]) -> str:
    """Сформировать D2-описание графа зависимостей.

    Рёбра направлены от зависимого пакета к его зависимости.
    Изолированные узлы объявляются явно, чтобы не потерялись.
    """
    lines: List[str] = ["direction: down"]
    for node in sorted(graph):
        deps = graph[node]
        if not deps:
            lines.append(_quote(node))
            continue
        for dep in sorted(deps):
            lines.append(f"{_quote(node)} -> {_quote(dep)}")
    return "\n".join(lines)


def reverse_graph_to_d2(
    graph: Dict[str, List[str]],
    target: str,
) -> str:
    """Сформировать D2-описание обратных зависимостей.

    Рёбра направлены от пакета-зависимости к целевому пакету:
    `parent -> target` означает «parent зависит от target».
    """
    reverse = build_reverse_index(graph)
    lines: List[str] = ["direction: down"]
    parents = sorted(reverse.get(target, []))
    if not parents:
        return "\n".join(lines + [_quote(target)])
    for parent in parents:
        lines.append(f"{_quote(parent)} -> {_quote(target)}")
    return "\n".join(lines)