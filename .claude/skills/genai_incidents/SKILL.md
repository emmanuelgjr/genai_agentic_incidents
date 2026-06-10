```markdown
# genai_incidents Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches you the core development patterns and workflows used in the `genai_incidents` TypeScript repository. You'll learn the project's file organization, code style, commit conventions, and how to participate in the automated weekly data refresh process. This guide is ideal for contributors looking to maintain consistency and efficiency in this codebase.

## Coding Conventions

### File Naming
- **Style:** kebab-case
- **Example:**  
  ```
  incident-summary.ts
  id-deprecations.json
  ```

### Import Style
- **Style:** Relative imports
- **Example:**
  ```typescript
  import { getIncidentData } from './incident-data';
  ```

### Export Style
- **Style:** Named exports
- **Example:**
  ```typescript
  export function summarizeIncidents() { ... }
  export const INCIDENT_STATUSES = ['open', 'closed'];
  ```

### Commit Messages
- **Type:** Conventional commits
- **Prefix Used:** `chore`
- **Example:**  
  ```
  chore: update incident data files
  ```

## Workflows

### Weekly Data Auto-Refresh
**Trigger:** When the weekly data auto-refresh job runs or is manually triggered to update incident records and associated visualizations.  
**Command:** `/refresh-data`

1. **Update core incident data files**
   - Update files such as:
     - `data/incidents.json`
     - `data/incidents.min.json`
     - `data/id_deprecations.json`
2. **Regenerate summary documentation**
   - Update `INCIDENTS.md` to reflect the latest data.
3. **Update or add new incident markdown files**
   - Add or modify files in `docs/incident/`, e.g., `docs/incident/INC-XXXXX.md`.
4. **Regenerate data files in docs/**
   - Update `docs/data/incidents.min.json`.
5. **Regenerate SVG chart visualizations**
   - Update or create SVGs in `docs/charts/` such as:
     - `owasp_asi.svg`
     - `owasp_llm.svg`
     - `severity_stack.svg`
     - `year_bar.svg`

**Example Directory Update:**
```
data/
  incidents.json
  incidents.min.json
  id_deprecations.json
docs/
  INCIDENTS.md
  data/
    incidents.min.json
  incident/
    INC-12345.md
  charts/
    owasp_asi.svg
    year_bar.svg
```

## Testing Patterns

- **Framework:** Unknown (not detected)
- **Test File Pattern:** Files matching `*.test.*`
- **Example:**
  ```
  incident-summary.test.ts
  ```
- **Typical Test Structure:**
  ```typescript
  // incident-summary.test.ts
  import { summarizeIncidents } from './incident-summary';

  describe('summarizeIncidents', () => {
    it('should return correct summary', () => {
      // test implementation
    });
  });
  ```

## Commands

| Command        | Purpose                                                      |
|----------------|-------------------------------------------------------------|
| /refresh-data  | Run the weekly data auto-refresh workflow manually           |
```
