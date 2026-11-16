"""Точка входа для запуска через `python -m src.pkgviz`."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())