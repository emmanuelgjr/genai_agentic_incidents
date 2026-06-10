```markdown
# genai_incidents Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill teaches the core development patterns and workflows used in the `genai_incidents` TypeScript repository. The project manages and processes incident data, generating various outputs such as JSON, markdown, and charts. You'll learn the repository's coding conventions, how to execute essential data rebuild workflows, and how to structure and run tests.

## Coding Conventions

### File Naming

- **Style:** kebab-case
- **Example:**  
  ```
  incident-processor.ts
  data-loader.ts
  ```

### Imports

- **Style:** Relative imports
- **Example:**
  ```typescript
  import { parseIncident } from './incident-parser';
  import { INCIDENTS } from '../data/incidents';
  ```

### Exports

- **Style:** Named exports
- **Example:**
  ```typescript
  // incident-processor.ts
  export function processIncident(data: IncidentData): ProcessedIncident { ... }
  export const INCIDENT_STATUS = { ... };
  ```

### Commit Messages

- **Style:** Conventional commits
- **Prefix:** `fix`
- **Example:**
  ```
  fix: correct incident date parsing for edge cases
  ```

## Workflows

### Full Data Rebuild and Site Output Sync

**Trigger:**  
When the incident data source is updated, corrupted, or out of sync with generated site outputs (e.g., after restoring a feed or fixing a build environment).

**Command:**  
`/rebuild-data-and-site`

**Step-by-step:**

1. **Restore or update data source files**  
   Update or restore files such as `cve_nvd_expanded.json` or `id_deprecations.json` as needed.

2. **Regenerate all processed data files**  
   Run the appropriate scripts or commands to regenerate:
   - `data/incidents.json`
   - `data/incidents.min.json`
   - `docs/data/incidents.min.json`
   - `src/genai_incidents/data/incidents.min.json`

3. **Regenerate all output artifacts**  
   Ensure the following outputs are rebuilt:
   - `INCIDENTS.md`
   - All SVG charts in `docs/charts/*.svg`
   - Per-incident markdown files in `docs/incident/INC-*.md`
   - Year shard files in `docs/incidents/*.md`

4. **Commit all regenerated files**  
   Add and commit all updated/generated files to the repository to ensure outputs match the data source.

**Files Involved:**
- `data/incidents.json`
- `data/incidents.min.json`
- `docs/data/incidents.min.json`
- `src/genai_incidents/data/incidents.min.json`
- `INCIDENTS.md`
- `docs/charts/*.svg`
- `docs/incident/INC-*.md`
- `docs/incidents/*.md`
- `ingest/cve_nvd_expanded.json`
- `data/id_deprecations.json`
- `src/genai_incidents/data/id_deprecations.json`

**Frequency:**  
~2x/month

**Example Command:**
```sh
/rebuild-data-and-site
```

## Testing Patterns

- **Test Files:**  
  Test files follow the `*.test.*` pattern (e.g., `incident-parser.test.ts`).
- **Framework:**  
  Not explicitly detected; follow common TypeScript testing practices.

**Example Test File:**
```typescript
// incident-parser.test.ts
import { parseIncident } from './incident-parser';

describe('parseIncident', () => {
  it('should parse valid incident data', () => {
    const input = { id: 'INC-001', ... };
    const result = parseIncident(input);
    expect(result.id).toBe('INC-001');
  });
});
```

## Commands

| Command                | Purpose                                                           |
|------------------------|-------------------------------------------------------------------|
| /rebuild-data-and-site | Rebuilds all incident data and regenerates site outputs           |
```
