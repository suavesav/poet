venv:
	pipenv sync
	pipenv sync --dev

test:
	python -m unittest discover

clean:
	pipenv --rm
	rm -rf .tox *.egg-info

pti:
	pipenv run ptipython --vi
