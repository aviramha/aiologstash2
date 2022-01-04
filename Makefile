SOURCES = aiologstash2 tests


test: pytest tests


lint: mypy black flake8


mypy:
	mypy --strict aiologstash2


black:
	isort -c $(SOURCES)
	black --check $(SOURCES)

flake8:
	flake8 $(SOURCES)

fmt:
	isort $(SOURCES)
	black $(SOURCES)
