# Host integration notes (T1 addition)

This note adapts the imported Anthropic skill for this repository; upstream examples and helper code remain intact.

- Use only an explicitly scoped local test application and synthetic accounts/data. Do not navigate authenticated production applications or execute writes merely because the skill is loaded.
- Confirm Python Playwright and its browser runtime exist before testing. Installing the skill installs neither. Use the host's supported browser tools only when equivalent behavior and permissions are clear.
- Prefer an already running, approved local server. The bundled with_server.py uses shell=True and only terminates its immediate child. Process-tree cleanup and pipe behavior are not verified on Windows; use the host's managed process lifecycle for Windows server startup instead of assuming that helper cleans up descendants.
- The generic upstream networkidle advice is not universal. Chat streams, polling and persistent connections may never become idle; wait for a specific page state/locator or controlled application readiness signal with a timeout.
- Upstream examples include /tmp and /mnt output paths. Choose a scoped absolute workspace output path valid on the current OS. Do not run the examples unchanged on unrelated pages.
- Assert observable user behavior, capture console/page/network failures, and distinguish an incomplete streamed answer from success. Clean up only test resources actually created.
- This import was statically reviewed and helper CLI error paths were exercised; no browser session or web application test was run during packaging.
