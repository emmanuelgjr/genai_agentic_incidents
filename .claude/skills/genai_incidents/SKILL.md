```markdown
# genai_incidents Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill teaches you the core development conventions and workflows for the `genai_incidents` Python repository. The project manages and publishes structured data about generative AI incidents, including incident metadata, documentation, and visualizations. You'll learn how to follow its coding style, update data and documentation, and use common project workflows.

## Coding Conventions

**File Naming**

- Files use kebab-case for naming (e.g., `merge-and-dedupe.py`, `id-deprecations.json`).

**Imports**

- Relative imports are preferred within the codebase.

  ```python
  from .utils import dedupe_incidents
  ```

**Exports**

- Named exports are used (i.e., functions/classes are explicitly exported).

  ```python
  # src/genai_incidents/utils.py
  def dedupe_incidents(incidents):
      ...
  ```

**Commit Messages**

- Follows [Conventional Commits](https://www.conventionalcommits.org/) with prefixes like `chore` and `fix`.
- Example:

  ```
  chore: update incident data and regenerate charts
  fix: correct date parsing for incident ingestion
  ```

## Workflows

### Data Release Workflow

**Trigger:** When you want to publish a new release with updated incident data and documentation.

**Command:** `/release-data`

1. **Update incident data files:**
   - Edit or regenerate `data/incidents.json`, `data/incidents.min.json`, and `src/genai_incidents/data/incidents.min.json` with the latest incident information.

2. **Update or generate deprecation/id mapping files:**
   - Ensure `data/id_deprecations.json` and `src/genai_incidents/data/id_deprecations.json` reflect any changes in incident IDs or deprecated entries.

3. **Update documentation files:**
   - Revise `INCIDENTS.md`, `CHANGELOG.md`, and `CITATION.cff` to document new incidents, changes, and citation info.

4. **Update or add incident markdown files:**
   - For each new or updated incident, create or update `docs/incident/INC-*.md`.

5. **Update summary/yearly documentation:**
   - Update `docs/incidents/YYYY.md` to summarize incidents for the current year.

6. **Update charts and visualizations:**
   - Regenerate or update SVG charts in `docs/charts/*.svg` to reflect the latest data.

7. **Update minified data for docs:**
   - Ensure `docs/data/incidents.min.json` is current.

8. **Update project metadata:**
   - Edit `pyproject.toml` if dependencies or project metadata have changed.

9. **Update or run scripts as needed:**
   - Use scripts like `scripts/merge_and_dedupe.py` to process and deduplicate incident data.

**Example: Running the Data Release Workflow**

```bash
# 1. Merge and deduplicate incidents
python scripts/merge_and_dedupe.py

# 2. Manually update documentation and charts as needed

# 3. Commit changes with a conventional commit message
git add .
git commit -m "chore: publish new incident data and update docs"
git push

# 4. (Optional) Use the command for automation
/release-data
```

## Testing Patterns

- Test files follow the pattern `*.test.*` (e.g., `dedupe.test.py`).
- The specific testing framework is not detected, but tests are likely written in Python.
- Example test file:

  ```python
  # dedupe.test.py
  from .dedupe import dedupe_incidents

  def test_dedupe_removes_duplicates():
      incidents = [...]
      result = dedupe_incidents(incidents)
      assert len(result) == expected_count
  ```

## Commands

| Command        | Purpose                                                        |
|----------------|----------------------------------------------------------------|
| /release-data  | Run the data release workflow to update incidents and docs     |
```
