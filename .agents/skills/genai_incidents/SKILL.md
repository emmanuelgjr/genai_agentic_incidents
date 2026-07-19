```markdown
# genai_incidents Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development patterns and conventions used in the `genai_incidents` TypeScript codebase. You'll learn about file naming, import/export styles, commit message conventions, and how to write and run tests. This guide is ideal for contributors looking to maintain code consistency and quality.

## Coding Conventions

### File Naming
- **Style:** Snake case
- **Example:**  
  ```plaintext
  incident_report.ts
  utils/helpers.ts
  ```

### Import Style
- **Relative imports are used throughout the codebase.**
- **Example:**
  ```typescript
  import { parseIncident } from './parser';
  import { formatDate } from '../utils/date_utils';
  ```

### Export Style
- **Named exports are preferred.**
- **Example:**
  ```typescript
  // In incident_report.ts
  export function createIncident() { ... }
  export const INCIDENT_STATUS = { ... };
  ```

### Commit Message Conventions
- **Conventional commits with type prefix.**
- **Common prefix:** `chore`
- **Average length:** ~32 characters
- **Example:**
  ```
  chore: update dependencies
  chore: fix typo in incident parser
  ```

## Workflows

### Commit Workflow
**Trigger:** When making any code change  
**Command:** `/commit`

1. Make your code changes following the coding conventions.
2. Stage your changes:  
   ```
   git add .
   ```
3. Write a commit message using the conventional format:  
   ```
   git commit -m "chore: short description of change"
   ```
4. Push your changes:  
   ```
   git push
   ```

### Testing Workflow
**Trigger:** Before pushing changes or submitting a pull request  
**Command:** `/test`

1. Identify test files (pattern: `*.test.*`).
2. Run your test suite using your preferred TypeScript testing tool (e.g., Jest, Mocha).  
   *(Note: The specific test runner is not detected; adjust as needed.)*
   ```
   npx jest
   ```
3. Ensure all tests pass before proceeding.

## Testing Patterns

- **Test files follow the pattern:** `*.test.*`
- **Example:**
  ```
  incident_parser.test.ts
  ```
- **Typical test structure:**
  ```typescript
  import { parseIncident } from './parser';

  describe('parseIncident', () => {
    it('should parse a valid incident', () => {
      // test implementation
    });
  });
  ```

## Commands

| Command   | Purpose                                      |
|-----------|----------------------------------------------|
| /commit   | Guide for making conventional commits        |
| /test     | Steps to run and verify tests                |
```
