.PHONY: clean-pyc clean-build test

all: clean sdist


clean: clean-build clean-pyc


clean-build:
	$(info # Removing build artefacts)
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	$(info # Removing pycies artefacts)
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

isort:
	$(info # Sorting imports)
	sh -c "isort --skip-glob=.tox --recursive . "

lint:
	flake8 --exclude=.tox


sdist: clean
	python setup.py sdist

pep8:
	autopep8 -aa --in-place --recursive --max-line-length=130 ./src

test:
	$(info # Testing with tox)
	tox
	flake8 ./src/

coverage:
	$(info # Test coverage)
	coverage run --source=./src/ -m py.test tests/ -v --tb=native
	coverage report

coverage-html: coverage
	coverage html

patch:
	bumpversion patch
	-git commit -am "patch versions"

git-clean:
	git clean -f -d

release: clean
	python setup.py bdist_wheel
	twine upload ./dist/* --verbose
