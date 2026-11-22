"""Тесты генерации D2-представления графа."""

from src.pkgviz.d2_render import graph_to_d2, reverse_graph_to_d2


def test_graph_to_d2_simple():
    graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    text = graph_to_d2(graph)
    lines = text.splitlines()
    assert lines[0] == "direction: down"
    assert "A -> B" in lines
    assert "A -> C" in lines
    assert "B -> D" in lines
    assert "C -> D" in lines
    assert "D" in lines  # изолированный узел объявлен


def test_graph_to_d2_empty_deps():
    graph = {"A": []}
    text = graph_to_d2(graph)
    assert "A" in text.splitlines()
    assert "->" not in text


def test_graph_to_d2_quotes_special_names():
    graph = {"libc6:amd64": ["libgcc-s1"]}
    text = graph_to_d2(graph)
    assert '"libc6:amd64" -> libgcc-s1' in text


def test_reverse_graph_to_d2():
    graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    text = reverse_graph_to_d2(graph, "D")
    lines = text.splitlines()
    assert lines[0] == "direction: down"
    assert "B -> D" in lines
    assert "C -> D" in lines


def test_reverse_graph_to_d2_no_parents():
    graph = {"A": ["B"], "B": []}
    text = reverse_graph_to_d2(graph, "A")
    assert "A" in text.splitlines()
    assert "->" not in text