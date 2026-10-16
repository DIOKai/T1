---
name: mobile-notifications-background
description: "Implement or debug local notifications, remote push delivery, notification navigation and OS-managed background work in Expo mobile apps. Use for reminder, push token, receipt, permission and background-sync tasks; not for exact-time server scheduling or silently enabling push services."
---

# Mobile Notifications and Background Work

## Select the right mechanism
Inspect Expo SDK, native configuration, platforms, existing credentials and delivery requirements. Read [sources](references/sources.md) and version-matched docs.
- Use local notifications for device-scheduled reminders.
- Use server push for remote events.
- Use OS-managed background work for deferrable refresh.
- Use a server scheduler for server work that must run independently of the phone.
Never promise exact background execution, delivery, or a permanently running mobile process. Do not silently adopt EAS, paid push vendors or cloud schedulers.

## Build the requested path
1. Ask for notification permission at a meaningful user action. Implement denied/provisional/disabled behavior and a settings path without repeated prompts. Keep the app usable without notification permission.
2. Use a supported development or release build for remote push testing; do not assume Expo Go supports all platforms/features. Check physical-device and simulator support against the selected SDK.
3. Register tokens on an authenticated backend with user/device/project/platform ownership and last-seen data. Handle token rotation and remove or detach tokens on logout. Do not include secrets in notifications or bind a supplied user ID without checking the session.
4. Configure Android channels and platform permissions for the actual target version. Configure APNs/FCM credentials only through authorized secret management; never commit service-account files or private keys.
5. Send using bounded concurrency and retries. Store Expo tickets and check receipts, retire DeviceNotRegistered tokens, and distinguish provider acceptance from display or user receipt. Use a stable event identifier and avoid duplicate processing.
6. Handle foreground display, background taps and cold-start taps. Validate notification payloads and deep-link destinations; require authentication/authorization before opening private content. Consume the launch response once and wait until navigation is ready.
7. For recurring reminders, specify calendar/time-zone semantics. Check daylight-saving transitions, device time changes, edited/canceled reminders and duplicates; cancel old schedules when replacing them. If precise Android alarm timing is required, check current exact-alarm eligibility, permissions and store policy instead of assuming ordinary notification scheduling qualifies.
8. Define background tasks in module scope as required by the SDK, register once, bound network work and persist progress. Save state on expiration. Treat force-quit, low power and vendor battery policies as normal constraints. Move durable work to an outbox or backend instead of depending on a timer.
9. Log redacted delivery status and task outcomes, not private message content. Loading this skill does not authorize sending a real notification or registering third-party accounts.

## Verify
Test permission accept/deny; local reminder edit/cancel; foreground/background/cold-start navigation; invalid destination; logout/account switch; stale token; transient failure and duplicate events. For background work use SDK debug triggers, then separately observe OS-triggered behavior on supported devices. A debug trigger is not proof of production timing.

Return platform/build, permission state, receipt evidence, task evidence and limitations. Do not report a push as delivered merely because the send endpoint returned success.
