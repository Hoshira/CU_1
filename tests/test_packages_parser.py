"""Тесты парсера Packages и извлечения зависимостей."""

from pathlib import Path

import pytest

from src.pkgviz.packages_parser import (
    extract_dependency_names,
    find_package,
    get_direct_dependencies,
    parse_packages,
)

FIXTURE = Path(__file__).parent / "fixtures" / "Packages.txt"


@pytest.fixture()
def packages_text():
    return FIXTURE.read_text(encoding="utf-8")


def test_parse_packages_returns_blocks(packages_text):
    packages = parse_packages(packages_text)
    assert len(packages) == 5
    assert packages[0]["Package"] == "bash"
    assert packages[1]["Package"] == "coreutils"
    assert packages[2]["Package"] == "base-files"
    assert packages[3]["Package"] == "multiline-deps"
    assert packages[4]["Package"] == "combined"


def test_parse_packages_concatenates_multiline_description(packages_text):
    packages = parse_packages(packages_text)
    bash = packages[0]
    assert "multiline description" in bash["Description"]


def test_find_package_existing(packages_text):
    packages = parse_packages(packages_text)
    pkg = find_package(packages, "bash", "5.1-6ubuntu1")
    assert pkg is not None
    assert pkg["Package"] == "bash"


def test_find_package_wrong_version(packages_text):
    packages = parse_packages(packages_text)
    assert find_package(packages, "bash", "9.9") is None


def test_extract_dependency_names_full_field():
    field = "base-files (>= 2.1.12), debianutils (>= 2.15), libc6 (>= 2.34)"
    names = extract_dependency_names(field)
    assert names == ["base-files", "debianutils", "libc6"]


def test_extract_dependency_names_with_alternatives():
    assert extract_dependency_names("foo | bar, baz") == ["foo", "baz"]


def test_extract_dependency_names_empty():
    assert extract_dependency_names("") == []


def test_get_direct_dependencies_success(packages_text):
    packages = parse_packages(packages_text)
    deps = get_direct_dependencies(packages, "bash", "5.1-6ubuntu1")
    assert deps == ["base-files", "debianutils", "libc6"]


def test_get_direct_dependencies_includes_pre_depends(packages_text):
    packages = parse_packages(packages_text)
    deps = get_direct_dependencies(packages, "coreutils", "8.32-4.1ubuntu1")
    assert "libacl1" in deps
    assert "libgmp10" in deps
    assert "libselinux1" in deps


def test_get_direct_dependencies_pre_depends_only(packages_text):
    packages = parse_packages(packages_text)
    deps = get_direct_dependencies(packages, "coreutils", "8.32-4.1ubuntu1")
    assert deps == [
        "libacl1", "libattr1", "libc6", "libgmp10", "libselinux1"
    ]


def test_get_direct_dependencies_multiline(packages_text):
    packages = parse_packages(packages_text)
    deps = get_direct_dependencies(packages, "multiline-deps", "1.0")
    assert deps == ["base-files", "debianutils", "libc6"]


def test_get_direct_dependencies_package_without_depends(packages_text):
    packages = parse_packages(packages_text)
    deps = get_direct_dependencies(packages, "base-files", "12ubuntu4")
    assert deps == []


def test_get_direct_dependencies_merges_pre_depends_and_depends(packages_text):
    packages = parse_packages(packages_text)
    deps = get_direct_dependencies(packages, "combined", "1.0")
    assert deps == ["pre-pkg", "dep-a", "dep-b"]


def test_get_direct_dependencies_package_not_found(packages_text):
    packages = parse_packages(packages_text)
    with pytest.raises(LookupError):
        get_direct_dependencies(packages, "bash", "9.9")