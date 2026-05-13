.PHONY: build validate render merge install clean ingest-cve

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

# Pull AI/ML/LLM/agent CVEs from NVD + GHSA + OSV.
# Output: ingest/cve_nvd_expanded.json
# Cached responses are stored under ingest/_cache/{nvd,ghsa,osv}/ so the
# script is restartable.  Requires `gh` CLI to be authenticated.
ingest-cve:
	python scripts/ingest_cve_nvd_expanded.py

clean:
	rm -f data/incidents.json data/incidents.min.json data/legacy_consolidated.json INCIDENTS.md
