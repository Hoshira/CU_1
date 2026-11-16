"""Загрузка файлов Packages.gz из репозитория Ubuntu."""

import gzip
import urllib.error
import urllib.request
from typing import Optional

from .errors import DataError

DEFAULT_DIST = "jammy"
DEFAULT_COMPONENT = "main"
DEFAULT_ARCH = "amd64"


def build_packages_url(
    repo_url: str,
    dist: str = DEFAULT_DIST,
    component: str = DEFAULT_COMPONENT,
    arch: str = DEFAULT_ARCH,
) -> str:
    """Построить URL файла Packages.gz по адресу репозитория."""
    base = repo_url.rstrip("/")
    return (
        f"{base}/dists/{dist}/{component}/binary-{arch}/Packages.gz"
    )


def fetch_packages_text(url: str, timeout: float = 30.0) -> str:
    """Скачать Packages.gz по URL и вернуть распакованный текст.

    Бросает DataError при сетевой ошибке или неверном формате.
    """
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            compressed = response.read()
    except urllib.error.HTTPError as exc:
        raise DataError(
            f"Репозиторий вернул HTTP {exc.code} для {url}"
        ) from exc
    except urllib.error.URLError as exc:
        raise DataError(
            f"Не удалось загрузить {url}: {exc.reason}"
        ) from exc

    try:
        return gzip.decompress(compressed).decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise DataError(
            f"Ответ {url} не является корректным gzip-архивом UTF-8"
        ) from exc


def load_packages(
    repo_url: str,
    dist: Optional[str] = None,
    component: Optional[str] = None,
    arch: Optional[str] = None,
) -> str:
    """Скачать Packages.gz с параметрами по умолчанию."""
    url = build_packages_url(
        repo_url,
        dist=dist or DEFAULT_DIST,
        component=component or DEFAULT_COMPONENT,
        arch=arch or DEFAULT_ARCH,
    )
    return fetch_packages_text(url)