---
name: code-review-notes
description: Produce structured code review notes for a code snippet or diff, covering correctness, security, and readability.
---

# Code Review Notes

When asked to review code or produce code review notes, ALWAYS follow this structure:

1. **Summary** — one sentence verdict: approve / approve with changes / request changes.
2. **Correctness** — up to three issues with logic, edge cases, or error handling. Write "None found" if clean.
3. **Security** — up to three issues (injection, auth, secrets, input validation, OWASP Top 10). Write "None found" if clean.
4. **Readability** — up to two suggestions on naming, structure, or documentation.
5. **Required changes** — numbered list of blockers before merge. Empty list if approving.

Rules:
- Be specific: cite the exact line or pattern, not vague advice.
- Total length under 300 words.
- No praise filler ("great job", "nice work"). State facts only.
- If a security issue is critical (e.g. exposed secret, SQL injection), mark it **[CRITICAL]**.
