.PHONY: test upload

test:
	tox

upload:
	python -m build
	python -m twine upload dist/*
