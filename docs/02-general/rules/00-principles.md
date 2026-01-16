# Core Principles

SCOPE: All code in this project
TOOLS: All

---

## YAGNI - You Aren't Gonna Need It

- Only implement features that are currently needed
- Don't add code "just in case"
- Remove dead code immediately
- Avoid premature abstraction

## KISS - Keep It Simple, Stupid

- Prefer simple solutions over clever ones
- Readable code > short code
- Avoid over-engineering
- One responsibility per function/class

## DRY - Don't Repeat Yourself

- Extract common patterns into reusable functions
- Use configuration over hardcoding
- Single source of truth for constants
- But don't over-abstract for minor duplication

---

## Code Quality Standards

1. **Type Safety**: Full type hints, no `Any` without justification
2. **Error Handling**: Explicit error types, no silent failures
3. **Testing**: Unit tests for business logic, integration tests for APIs
4. **Documentation**: Self-documenting code, comments for "why" not "what"

---

## File Organization

- Keep files under 200 lines
- One module = one responsibility
- Use descriptive kebab-case filenames
- Group by feature, not by type

---

## Security

- Never commit secrets
- Use SecretStr for sensitive config
- Validate all external input
- Log securely (no PII, tokens)
