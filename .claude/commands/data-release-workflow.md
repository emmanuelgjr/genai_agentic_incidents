---
name: data-release-workflow
description: Workflow command scaffold for data-release-workflow in genai_incidents.
allowed_tools: ["Bash", "Read", "Write", "Grep", "Glob"]
---

# /data-release-workflow

Use this workflow when working on **data-release-workflow** in `genai_incidents`.

## Goal

Publishes a new data release, updating incident data, changelogs, charts, and documentation to reflect the latest incidents and metadata.

## Common Files

- `data/incidents.json`
- `data/incidents.min.json`
- `data/id_deprecations.json`
- `src/genai_incidents/data/incidents.min.json`
- `src/genai_incidents/data/id_deprecations.json`
- `INCIDENTS.md`

## Suggested Sequence

1. Understand the current state and failure mode before editing.
2. Make the smallest coherent change that satisfies the workflow goal.
3. Run the most relevant verification for touched files.
4. Summarize what changed and what still needs review.

## Typical Commit Signals

- Update incident data files (data/incidents.json, data/incidents.min.json, src/genai_incidents/data/incidents.min.json)
- Update or generate deprecation/id mapping files (data/id_deprecations.json, src/genai_incidents/data/id_deprecations.json)
- Update documentation files (INCIDENTS.md, CHANGELOG.md, CITATION.cff)
- Update or add incident markdown files (docs/incident/INC-*.md)
- Update summary/yearly documentation (docs/incidents/YYYY.md)

## Notes

- Treat this as a scaffold, not a hard-coded script.
- Update the command if the workflow evolves materially.