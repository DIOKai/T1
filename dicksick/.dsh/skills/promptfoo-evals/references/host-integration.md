# Host integration notes (T1 addition)

Preserve the existing target and cost rules. Installing a skill does not authorize model, grader or remote validation calls.

For this repository default to explicit local fixtures/echo and deterministic assertions. Do not run paid targets or graders, create accounts, enable fallback providers, or install/upgrade an npm package merely by loading this skill. Use an already installed CLI when available and record its version.

promptfoo-provider-setup is included as a companion. Redteam skills referenced by upstream are not included in this batch; do not claim those workflows are available or run remote redteam generation.

--no-share controls result sharing, not all network access. A local wrapper can still call a remote service: inspect its implementation and configuration. Fixture pass/fail checks only validate harness wiring, never actual model quality. Retain controls that detect wrong answers and grader/transport errors.

Unix shell/CI examples need adaptation to the host environment; paths and output destinations must remain scoped. Upstream references contain paid model examples for illustration only; they are not selected or configured here.
