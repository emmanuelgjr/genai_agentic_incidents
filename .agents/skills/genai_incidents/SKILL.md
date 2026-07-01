```markdown
# genai_incidents Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development conventions and workflows used in the `genai_incidents` TypeScript codebase. It covers file naming, import/export styles, commit message patterns, and testing approaches. By following these guidelines, contributors can ensure consistency and maintainability across the project.

## Coding Conventions

### File Naming
- Use **snake_case** for all file names.
  - **Example:**  
    ```
    incident_report.ts
    utils/helpers.ts
    ```

### Import Style
- Use **relative imports** for referencing modules.
  - **Example:**
    ```typescript
    import { parseIncident } from './parser';
    import { formatDate } from '../utils/date_utils';
    ```

### Export Style
- Use **named exports** rather than default exports.
  - **Example:**
    ```typescript
    // In parser.ts
    export function parseIncident(data: string): Incident { ... }
    export function validateIncident(incident: Incident): boolean { ... }
    ```

### Commit Messages
- Follow the **Conventional Commits** standard.
- Use the `feat` prefix for new features.
- Keep commit messages concise (average ~67 characters).
  - **Example:**
    ```
    feat: add incident parsing logic for new data format
    ```

## Workflows

### Feature Development
**Trigger:** When implementing a new feature  
**Command:** `/feature-development`

1. Create a new branch for your feature.
2. Write code following the coding conventions.
3. Add or update relevant tests (`*.test.*` files).
4. Commit changes using the `feat:` prefix and a concise message.
5. Open a pull request for review.

### Testing
**Trigger:** When verifying changes or before merging  
**Command:** `/run-tests`

1. Ensure all test files follow the `*.test.*` naming pattern.
2. Run the test suite using the project's test runner.
3. Review test results and fix any failures.
4. Commit any necessary test updates.

## Testing Patterns

- Test files are named using the `*.test.*` pattern (e.g., `incident_parser.test.ts`).
- The specific testing framework is not defined, but tests should be colocated with or near the code they test.
- Example test file:
  ```typescript
  // incident_parser.test.ts
  import { parseIncident } from './parser';

  describe('parseIncident', () => {
    it('should parse valid incident data', () => {
      const data = '...';
      const result = parseIncident(data);
      expect(result).toBeDefined();
    });
  });
  ```

## Commands
| Command              | Purpose                                      |
|----------------------|----------------------------------------------|
| /feature-development | Start a new feature development workflow     |
| /run-tests           | Run the test suite for the codebase          |
```
