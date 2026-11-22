"""Построение графа зависимостей итеративным DFS."""

from typing import Callable, Dict, List, Set, Tuple


def build_reverse_index(
    graph: Dict[str, List[str]],
) -> Dict[str, List[str]]:
    """Построить обратный индекс: пакет -> кто от него зависит.

    Для каждого ребра A -> B добавляем B -> A.
    """
    reverse: Dict[str, List[str]] = {}
    for node, deps in graph.items():
        reverse.setdefault(node, [])
        for dep in deps:
            reverse.setdefault(dep, [])
            if node not in reverse[dep]:
                reverse[dep].append(node)
    return reverse


def collect_reverse_dependencies(
    graph: Dict[str, List[str]],
    target: str,
) -> List[str]:
    """Собрать все пакеты, которые (транзитивно) зависят от target.

    Использует итеративный DFS без рекурсии — тот же приём, что и
    build_graph_dfs, но по обратному индексу.
    """
    reverse = build_reverse_index(graph)
    visited: Set[str] = {target}
    stack: List[str] = [target]
    result: List[str] = []

    while stack:
        node = stack.pop()
        for parent in reverse.get(node, []):
            if parent in visited:
                continue
            visited.add(parent)
            result.append(parent)
            stack.append(parent)

    return result


def build_graph_dfs(
    root: str,
    get_deps: "Callable[[str], List[str]]",
) -> Dict[str, List[str]]:
    """Построить граф обходом DFS без рекурсии (явный стек).

    Каждый пакет раскрывается один раз — цикл не зацикливает обход.
    """
    graph: Dict[str, List[str]] = {}
    visited: Set[str] = set()
    stack: List[str] = [root]

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        deps = get_deps(node)
        graph[node] = deps
        for dep in deps:
            if dep not in visited:
                stack.append(dep)

    return graph


def find_cycles(
    graph: Dict[str, List[str]],
    root: str,
) -> List[List[str]]:
    """Найти циклы в графе итеративным DFS с раскраской вершин.

    Белая — не посещена, серая — в текущем стеке, чёрная — завершена.
    Ребро в серую вершину означает цикл.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: Dict[str, int] = {node: WHITE for node in graph}
    cycles: List[List[str]] = []

    # Стек: (узел, индекс следующей зависимости, путь от корня)
    stack: List[tuple] = [(root, 0, [root])]
    color[root] = GRAY

    while stack:
        node, idx, path = stack[-1]

        if idx < len(graph.get(node, [])):
            dep = graph[node][idx]
            stack[-1] = (node, idx + 1, path)

            if dep not in color:
                # пакет вне обхода — раскрываем как новый
                color[dep] = WHITE
                graph.setdefault(dep, [])

            if color[dep] == WHITE:
                color[dep] = GRAY
                stack.append((dep, 0, path + [dep]))
            elif color[dep] == GRAY:
                # нашли цикл: от dep до текущего узла
                start = path.index(dep)
                cycles.append(path[start:] + [dep])
        else:
            color[node] = BLACK
            stack.pop()

    return cycles