.PHONY: load validate test clean report dashboard api ratios

load:
	python src/main.py load

validate:
	python src/main.py validate

test:
	pytest tests/

clean:
	python src/main.py clean

report:
	python src/main.py report

dashboard:
	python src/main.py dashboard

api:
	python src/main.py api

ratios:
	python src/main.py ratios