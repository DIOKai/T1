---
name: deepseek-app-integration
description: "Implement or review DeepSeek-backed mobile and web app features: backend API proxy, streamed answers, tool calls, cancellation, bounded retries, rate limits and usage budgets. Use for DeepSeek integration or failures; not for replacing the coding agent provider or provisioning keys."
---

# DeepSeek App Integration

## Scope and preflight
Inspect the app, backend, package lock, existing AI adapter and tests. Determine which endpoint format and SDK are actually used. Read [sources](references/sources.md), then fetch current official documentation for the selected model and endpoint; do not hardcode remembered model names, pricing or parameter support.

Follow the repository's existing permission and spending rules. This skill installs nothing and makes no paid call merely by being loaded. Use existing authorized credentials through the backend environment; never request that the user paste keys into chat. Do not create accounts, top up balances, switch providers or edit coding-agent configuration as a side effect.

## Implementation sequence
1. Define the feature contract: accepted input, maximum input/output, authenticated user, response schema, cancellation, expected latency and maximum per-user spend. If requirements are missing, make a plan and use local fixtures until resolved.
2. Keep the provider key on the backend. Never bundle it in Expo public variables, browser JavaScript, mobile assets or source control. Authenticate the caller, authorize each conversation/resource, and enforce quotas before the provider request.
3. Implement a provider adapter that isolates model, base URL, endpoint format and SDK-specific parameters from product code. Treat OpenAI compatibility as partial: check the supported parameters for the actual endpoint.
4. For Chat Completions thinking mode with tools, preserve the protocol-required assistant fields and reasoning_content in server-side request history as documented. Without tools, do not assume the same replay rules. Keep protocol state separate from displayed answer text; do not log raw protocol reasoning or secrets. Do not force unsupported tool_choice settings.
5. For streaming, use an incremental SSE parser, handling split UTF-8 characters, partial lines/events, empty deltas, finish events and errors after headers. Separate answer content from protocol metadata. Show interrupted output as incomplete with an explicit retry action; distinguish output-limit completion from a transport error. Propagate client cancellation to the backend/provider where supported; do not promise cancellation reverses charges.
6. Validate every tool name and argument against an allowlist and schema; enforce authorization in the tool implementation. Treat model output as untrusted. Bound tool rounds, time, output and concurrency. Require existing product approval for destructive or person-directed tools.
7. Classify errors: 400/422 require request correction; 401 requires credential diagnosis; 402 is a balance issue, not an automatic top-up. Retry 429 and transient network/500/503 failures only within an explicit attempt/time budget using backoff and jitter, respecting Retry-After if supplied. Never restart a partially emitted stream invisibly or repeat a side-effecting tool without deduplication.
8. Record redacted request identifiers, status, latency, model and returned usage. Estimate costs using current provider rates and mark estimates; reserve budget for concurrent in-flight calls. Do not cache or mix private answers across users.

## Verification
Use mocked transport first. Test fragmented SSE, cancellation, malformed JSON/tool arguments, an unauthorized conversation, 401/402, 429 recovery, retry exhaustion and a failed stream after partial text. Confirm duplicate delivery cannot execute a tool twice. Run one bounded live smoke test only if credentials and spend are already authorized; otherwise label it unverified.

Return changed files, endpoint/model/version, tests with evidence, unresolved risks and whether any live billable request occurred. Never claim an API key or paid service was configured when only scaffolding was written.
