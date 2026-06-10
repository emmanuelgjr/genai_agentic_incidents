```markdown
# genai_incidents Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill provides guidance for contributing to the `genai_incidents` repository, a TypeScript project focused on managing, enriching, and visualizing incident data (such as CVEs and related metadata). It covers coding conventions, data refresh workflows, testing patterns, and recommended commands for maintaining consistency and quality in the codebase.

## Coding Conventions

### File Naming

- Use **kebab-case** for all file and directory names.

  **Example:**
  ```
  data/incidents.json
  utils/data-loader.ts
  docs/incident/INC-1234.md
  ```

### Import Style

- Use **relative imports** for all modules.

  **Example:**
  ```typescript
  import { enrichIncident } from './utils/enrich-incident';
  import { INCIDENTS } from '../data/incidents';
  ```

### Export Style

- Prefer **named exports** over default exports.

  **Example:**
  ```typescript
  // Good
  export function enrichIncident(data: IncidentData): Incident { ... }

  // Avoid
  export default function enrichIncident(data: IncidentData): Incident { ... }
  ```

### Commit Messages

- Use **conventional commit** format, with the `feat` prefix for new features.

  **Example:**
  ```
  feat: add enrichment for CVSS vector parsing
  ```

## Workflows

### Bulk Incident Data Refresh

**Trigger:** When updating the incident database with new or enriched data (e.g., new CVEs, updated CVSS vectors, or additional metadata).

**Command:** `/refresh-incidents`

**Steps:**

1. **Update core incident data files**
   - Edit `data/incidents.json` and `data/id_deprecations.json` to add or update incident records.
2. **Regenerate minified and derived data files**
   - Run the appropriate scripts to produce `data/incidents.min.json` and `docs/data/incidents.min.json`.
3. **Update or add incident markdown files**
   - For each new or updated incident, create or modify a markdown file under `docs/incident/` (e.g., `docs/incident/INC-1234.md`).
4. **Update summary documentation**
   - Revise `INCIDENTS.md` to reflect the latest changes.
5. **Regenerate charts and visualizations**
   - Use scripts or tools to update SVG charts in `docs/charts/` to visualize the new data.

**Example File Update:**
```json
// data/incidents.json
[
  {
    "id": "INC-1234",
    "title": "Example Incident",
    "cvss": "7.5",
    "description": "Details about the incident..."
  }
]
```

**Example Markdown:**
```markdown
<!-- docs/incident/INC-1234.md -->
# INC-1234: Example Incident

- **CVSS:** 7.5
- **Description:** Details about the incident...
```

## Testing Patterns

- Test files follow the pattern `*.test.*` (e.g., `enrich-incident.test.ts`).
- The specific testing framework is not detected, but tests are colocated with or near the code they verify.

**Example Test File:**
```
utils/enrich-incident.test.ts
```

**Example Test (TypeScript):**
```typescript
import { enrichIncident } from './enrich-incident';

describe('enrichIncident', () => {
  it('should enrich incident data with CVSS score', () => {
    const input = { id: 'INC-1234', cvss: '7.5' };
    const result = enrichIncident(input);
    expect(result.cvssScore).toBe(7.5);
  });
});
```

## Commands

| Command            | Purpose                                                        |
|--------------------|----------------------------------------------------------------|
| /refresh-incidents | Refresh and enrich incident data, updating all related assets. |

```