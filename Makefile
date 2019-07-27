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

requirements.txt: clean
	pipenv sync
	pipenv run pip freeze > requirements.txt
