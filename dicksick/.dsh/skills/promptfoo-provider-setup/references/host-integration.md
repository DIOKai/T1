# Host integration notes (T1 addition)

Use the existing authorization and free-only rules. Prefer local OpenAPI files and synthetic/mock responses. Do not run validate target or a remote provider/grader without an applicable explicit authorization; these are not static validation.

The bundled OpenAPI generator can create a local configuration without a network request. Its output is a draft, not a verified authentication boundary or full JSON Schema validator. Review response selectors, fixed identity, URLs, field examples and proposed secrets before use.

Do not copy real example credentials from a spec into a report. --token-env names an environment variable, not the secret value. Keep generated output in a new scoped path; the upstream --output option can overwrite a file.

Only the provider-setup and evals skills are imported from Promptfoo. Redteam references remain optional/unavailable. On Windows use actual absolute Node/Python paths and host-appropriate commands; do not execute Unix initialization snippets automatically.
