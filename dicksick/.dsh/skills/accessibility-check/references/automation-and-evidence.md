# Automation and evidence

Use [Playwright's accessibility testing guide](https://playwright.dev/docs/accessibility-testing) for integration with the installed @axe-core/playwright version. Confirm rule tags supported by that release and the agreed target; a version label alone does not prove all success criteria were checked.

Scope an application state and use rendered locators. Wait for meaningful readiness, then record browser/version, URL/state, rule IDs, impact, nodes, evidence and any exclusions. If excluding a known defect, retain its reason and tracking item; do not change exclusions to make the suite pass.

Avoid passing output merely because a result array is absent or empty after an error. Audit frames/shadow content only where supported, and report coverage gaps. Do not remove failing checks or weaken assertions without a requirement-based reason. Screenshots complement DOM/behavior evidence but do not prove keyboard or screen-reader behavior.

Candidate reviewed: [kylane/a11y-audit](https://github.com/kylane/a11y-audit). This independently written skill does not copy its long entrypoint, host-specific MCP instructions, update checks or automatic fix behavior. No source candidate code is executed.

For product/legal conformance decisions consult the applicable official standard and project requirements; this workflow reports evidence, not certification.
