#!/bin/bash
find . -name "*.py[co]" -o -name __pycache__ -exec rm -rf {} +
rm -R dist/
python setup.py sdist
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
