"""Тесты построения URL и загрузки Packages.gz."""

import gzip

import pytest

from src.pkgviz.errors import DataError
from src.pkgviz.repository import build_packages_url, fetch_packages_text


def test_build_packages_url_defaults():
    url = build_packages_url("http://archive.ubuntu.com/ubuntu")
    assert url == (
        "http://archive.ubuntu.com/ubuntu/dists/jammy/"
        "main/binary-amd64/Packages.gz"
    )


def test_build_packages_url_trims_trailing_slash():
    url = build_packages_url("http://archive.ubuntu.com/ubuntu/")
    assert url.endswith("/Packages.gz")
    assert "//dists" not in url


def test_build_packages_url_custom_params():
    url = build_packages_url(
        "http://archive.ubuntu.com/ubuntu",
        dist="focal",
        component="universe",
        arch="arm64",
    )
    assert "/dists/focal/universe/binary-arm64/Packages.gz" in url


def test_fetch_packages_text_raises_data_error_for_bad_url():
    with pytest.raises(DataError):
        fetch_packages_text("http://invalid.invalid/Packages.gz", timeout=1)


def test_fetch_packages_text_decompresses_gzip(tmp_path):
    """Локальная проверка распаковки через file:// URL."""
    raw = b"Package: bash\nVersion: 1.0\n"
    gz_path = tmp_path / "Packages.gz"
    gz_path.write_bytes(gzip.compress(raw))

    url = gz_path.resolve().as_uri()
    text = fetch_packages_text(url)
    assert "Package: bash" in text