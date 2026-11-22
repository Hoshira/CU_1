"""Тесты итеративного DFS и поиска циклов."""

from pathlib import Path

from src.pkgviz.graph import build_graph_dfs, find_cycles
from src.pkgviz.test_repo_parser import parse_test_repo
from src.pkgviz.graph import (
    build_graph_dfs,
    build_reverse_index,
    collect_reverse_dependencies,
    find_cycles,
)


FIXTURES = Path(__file__).parent / "fixtures"


def test_build_reverse_index_simple():
    graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    reverse = build_reverse_index(graph)
    assert set(reverse["D"]) == {"B", "C"}
    assert reverse["A"] == []


def test_collect_reverse_dependencies_transitive():
    graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    parents = collect_reverse_dependencies(graph, "D")
    assert set(parents) == {"A", "B", "C"}


def test_collect_reverse_dependencies_none():
    graph = {"A": ["B"], "B": []}
    assert collect_reverse_dependencies(graph, "A") == []


def test_collect_reverse_dependencies_cycle():
    graph = {"A": ["B"], "B": ["C"], "C": ["A"]}
    parents = collect_reverse_dependencies(graph, "A")
    assert set(parents) == {"B", "C"}


def test_build_graph_dfs_simple():
    deps_map = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    graph = build_graph_dfs("A", lambda n: deps_map[n])
    assert set(graph) == {"A", "B", "C", "D"}
    assert graph["A"] == ["B", "C"]


def test_build_graph_dfs_handles_cycle():
    deps_map = {"A": ["B"], "B": ["C"], "C": ["A"]}
    graph = build_graph_dfs("A", lambda n: deps_map[n])
    assert set(graph) == {"A", "B", "C"}
    # обход не зациклился — A раскрыт один раз


def test_find_cycles_detects_three_node_cycle():
    deps_map = {"A": ["B"], "B": ["C"], "C": ["A"]}
    graph = build_graph_dfs("A", lambda n: deps_map[n])
    cycles = find_cycles(graph, "A")
    assert any(set(c) >= {"A", "B", "C"} for c in cycles)


def test_find_cycles_none_in_simple():
    deps_map = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    graph = build_graph_dfs("A", lambda n: deps_map[n])
    assert find_cycles(graph, "A") == []


def test_parse_test_repo_simple():
    deps_map = parse_test_repo(str(FIXTURES / "test_graph_simple.txt"))
    assert deps_map["A"] == ["B", "C"]
    assert deps_map["D"] == []


def test_parse_test_repo_cycle():
    deps_map = parse_test_repo(str(FIXTURES / "test_graph_cycle.txt"))
    assert deps_map["C"] == ["A"]