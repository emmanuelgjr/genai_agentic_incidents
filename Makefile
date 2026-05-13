.PHONY: build validate render merge install clean

install:
	pip install -r requirements.txt

build: merge render validate

merge:
	python scripts/parse_existing.py
	python scripts/merge_and_dedupe.py

render:
	python scripts/render_markdown.py

validate:
	python scripts/validate.py

clean:
	rm -f data/incidents.json data/incidents.min.json data/legacy_consolidated.json INCIDENTS.md
