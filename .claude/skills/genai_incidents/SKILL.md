```markdown
# genai_incidents Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development conventions and workflows for the `genai_incidents` TypeScript codebase. You'll learn how to structure files, write and export code, follow commit message standards, and run tests in alignment with the project's established patterns.

## Coding Conventions

### File Naming
- Use **camelCase** for file names.
  - Example: `incidentHandler.ts`, `userProfile.ts`

### Import Style
- Use **relative imports** for internal modules.
  ```typescript
  import { getIncident } from './incidentHandler';
  ```

### Export Style
- Use **named exports**.
  ```typescript
  // incidentHandler.ts
  export function getIncident(id: string) { ... }
  export function listIncidents() { ... }
  ```

### Commit Messages
- Follow the **Conventional Commits** format.
- Use the `feat` prefix for new features.
  ```
  feat: add incident severity classification to handler
  ```

## Workflows

### Adding a New Feature
**Trigger:** When implementing a new feature or module  
**Command:** `/add-feature`

1. Create a new file using camelCase (e.g., `newFeature.ts`).
2. Write your code using named exports.
3. Use relative imports for any dependencies.
4. Write corresponding tests in a file named `newFeature.test.ts`.
5. Commit your changes with a message like:  
   `feat: short description of the new feature`
6. Open a pull request for review.

### Running Tests
**Trigger:** When verifying code correctness  
**Command:** `/run-tests`

1. Ensure your test files follow the `*.test.*` naming pattern (e.g., `incidentHandler.test.ts`).
2. Use the project's test runner (framework unknown; check project scripts or documentation).
3. Run the test command in your terminal (e.g., `npm test` or similar).

## Testing Patterns

- Test files are named with the pattern `*.test.*` (e.g., `incidentHandler.test.ts`).
- The testing framework is not specified; check the project documentation or `package.json` for details.
- Place test files alongside or near the code they test.

  ```typescript
  // incidentHandler.test.ts
  import { getIncident } from './incidentHandler';

  test('should retrieve incident by ID', () => {
    // test implementation
  });
  ```

## Commands
| Command       | Purpose                                   |
|---------------|-------------------------------------------|
| /add-feature  | Start the workflow for adding a new feature|
| /run-tests    | Run all tests in the codebase             |
```