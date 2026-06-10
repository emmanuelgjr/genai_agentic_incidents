```markdown
# genai_incidents Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development conventions and workflows used in the `genai_incidents` Python repository. The codebase follows consistent file naming, import/export styles, and commit message patterns to ensure maintainability and clarity. While no specific frameworks are detected, the repository emphasizes clean organization and testing practices.

## Coding Conventions

### File Naming
- All files use **kebab-case** (lowercase words separated by hyphens).
  - **Example:**  
    ```
    incident-handler.py
    data-loader.py
    ```

### Import Style
- **Relative imports** are used throughout the codebase.
  - **Example:**
    ```python
    from .utils import parse_incident
    from ..models.incident import Incident
    ```

### Export Style
- **Named exports** are preferred. Functions and classes are explicitly exported.
  - **Example:**
    ```python
    def process_incident(data):
        # processing logic
        return result

    __all__ = ["process_incident"]
    ```

### Commit Messages
- **Conventional commit** style is enforced.
- Prefixes like `refactor` are used, followed by a concise description (~70 chars).
  - **Example:**
    ```
    refactor: improve incident parsing logic for edge cases
    ```

## Workflows

### Refactor Code
**Trigger:** When improving, restructuring, or optimizing existing code without changing its external behavior.  
**Command:** `/refactor`

1. Identify code that needs refactoring.
2. Make improvements while ensuring no change in functionality.
3. Use relative imports and maintain kebab-case file naming.
4. Write a commit message using the `refactor:` prefix.
5. Run tests to verify no regressions.
6. Push changes to the repository.

## Testing Patterns

- **Test files** follow the pattern `*.test.*` (e.g., `incident-handler.test.py`).
- The testing framework is not explicitly specified; ensure tests are discoverable using this pattern.
- Tests should import modules using relative imports.
  - **Example:**
    ```python
    from ..incident-handler import process_incident

    def test_process_incident_valid():
        # test logic
        assert process_incident(valid_data) == expected
    ```

## Commands
| Command    | Purpose                                         |
|------------|-------------------------------------------------|
| /refactor  | Start a refactor workflow for code improvements |
```
