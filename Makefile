.PHONY: run test lint clean

run:
	python -m src.pkgviz --package requests --repo https://github.com/psf/requests --mode remote --version 2.31.0

test:
	python -m pytest tests/ -v

lint:
	python -m py_compile src/pkgviz/*.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +