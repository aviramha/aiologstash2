SOURCES = aiologstash2 tests


test: lint
	pytest tests


lint: mypy black flake8


mypy:
	mypy --strict aiologstash2


black:
	isort -c -rc $(SOURCES)
	black --check $(SOURCES)

flake8:
	flake8 $(SOURCES)

fmt:
	isort -rc $(SOURCES)
	black $(SOURCES)
