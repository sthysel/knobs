.PHONY: clean-pyc clean-build test

clean: clean-build clean-pyc

devtools: dev-requirements.txt
	pip install -r dev-requirements.txt

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

release: clean
	python setup.py bdist_wheel
	twine upload ./dist/*

sdist: clean
	python setup.py sdist
	ls -l dist

wheel: clean
	python setup.py bdist_wheel
	ls -l dist

test:
	pip install -e .
	tox
	flake8 ./src/

coverage:
	coverage run --source=./src/ -m py.test tests/ -v --tb=native
	coverage report

coverage-html: coverage
	coverage html

patch:
	bumpversion patch

