.PHONY: build validate render merge install clean test stix taxii misp huggingface ingest-cve ingest-kev ingest-airi ingest-aiaaic ingest-oecd-aim ingest-redteam ingest-all

install:
	pip install -r requirements.txt

build: merge render validate

test:
	pytest tests -q

merge:
	python scripts/parse_existing.py
	python scripts/merge_and_dedupe.py

render:
	python scripts/render_markdown.py

validate:
	python scripts/validate.py

# STIX 2.1 bundle for threat-intel platforms (build artifact, not committed).
stix:
	python scripts/export_stix.py

# Static TAXII 2.1 endpoint under docs/taxii2/ (Pages artifact, not committed).
taxii:
	python scripts/export_taxii.py

# MISP feed under docs/misp/ (Pages artifact, not committed).
misp:
	python scripts/export_misp.py

# Hugging Face dataset package (dist/hf/); add --push with HF_TOKEN set to upload.
huggingface:
	python scripts/export_huggingface.py

# Pull AI/ML/LLM/agent CVEs from NVD + GHSA + OSV.
# Output: ingest/cve_nvd_expanded.json
# Cached responses are stored under ingest/_cache/{nvd,ghsa,osv}/ so the
# script is restartable.  Requires `gh` CLI to be authenticated.
ingest-redteam:
	python scripts/ingest_redteam_benchmarks.py

ingest-cve:
	python scripts/ingest_cve_nvd_expanded.py

# Refresh the CISA Known Exploited Vulnerabilities snapshot.
# Output: ingest/cisa_kev.json
ingest-kev:
	python scripts/ingest_cisa_kev.py

# Pull the MIT FutureTech AI Risk Navigator dataset (wraps AIID with extra
# taxonomy and authoritative incident dates).
# Output: ingest/airi_navigator_incidents.json
ingest-airi:
	python scripts/ingest_airi_navigator.py

# Pull the canonical AIAAIC Repository spreadsheet (~2,200 rows).
# Output: ingest/aiaaic_sheet_incidents.json
ingest-aiaaic:
	python scripts/ingest_aiaaic_sheet.py

# Scrape the OECD AI Incidents Monitor (10k+ pages from the sitemap).
# Cached under ingest/_cache/oecd_aim/ so the script is restartable.
# Override OECD_AIM_LIMIT to control how many URLs to fetch (0 = all).
# Output: ingest/oecd_aim_full_incidents.json
ingest-oecd-aim:
	python scripts/ingest_oecd_aim.py

# Refresh every external source. Heavy: NVD/GHSA, AIRI, AIAAIC, OECD AIM.
ingest-all: ingest-cve ingest-kev ingest-airi ingest-aiaaic ingest-oecd-aim
	python scripts/scrape_aiid.py

clean:
	rm -f data/incidents.json data/incidents.min.json data/legacy_consolidated.json INCIDENTS.md
