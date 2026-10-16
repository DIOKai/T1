---
name: mobile-purchases-subscriptions
description: "Implement or audit native iOS/Android in-app purchases and subscription entitlement handling, verification, restore, pending states, renewals, refunds and sandbox tests. Use for StoreKit or Play Billing features; not for automatically adopting RevenueCat, creating paid accounts or making live purchases."
---

# Mobile Purchases and Subscriptions

## Choose a permitted integration
Read [sources](references/sources.md), inspect platform/framework/SDK, existing billing integration, product IDs, account model and backend. Determine whether this is a consumable, non-consumable, subscription or a physical-goods checkout; check current store rules for category and region.

Use the existing native StoreKit/Play Billing integration or an already authorized provider. RevenueCat has official skills, but that does not authorize adopting its hosted service, entering a paid plan or migrating the app. Never install a native billing library without checking framework/SDK support. Loading this skill permits no real purchase, refund or store submission.

## Design before charging
1. Define product-to-entitlement mapping and the source of truth. Separate catalog/offering display from verified access. Load localized prices and periods from the store rather than inventing currency strings.
2. Specify UI states: loading, unavailable, initiating, pending, canceled, verified, expired and failed. Pending or client-success UI alone must not grant paid access.
3. Verify transaction evidence with trusted store APIs or the selected backend verifier before granting server-managed benefits. Bind store transactions/purchase tokens to the authenticated account; reject replay and conflicting account ownership. Do not trust a client flag or unsigned callback.
4. Make event processing idempotent and transactional. Handle duplicate/out-of-order server notifications by querying current store state and recording stable transaction/event identifiers. Keep a ledger for consumable grants; access must not be duplicated by retries. Deduplicate both notification event IDs and the underlying purchase/fulfillment transaction: different events can describe the same purchase.
5. For Play, use current product/subscription verification endpoints and acknowledge/consume according to product type and the actual API contract. Do not consume non-consumables or pending purchases. For StoreKit, verify supported transaction evidence and finish only after the durable delivery decision; do not mix StoreKit 1 and 2 recipes blindly.
6. Derive subscription access from verified state and expiration/grace rules, not a local timer or one boolean. Handle renewal, cancel-at-period-end, expiration, grace/account-hold, refund/revocation, upgrade/downgrade and billing recovery separately. Cancellation is not always immediate expiration.
7. Implement restore/reconciliation and launch/resume transaction updates, not just button callbacks. Explain account conflicts without transferring a purchase to another app account automatically. Observe platform limitations for consumable restoration.
8. Preserve a bounded, explicit offline entitlement policy appropriate to risk; do not grant permanent access from a mutable local cache. Redact purchase tokens and payment details in logs.

## Verification
Use sandbox/test products and test accounts; distinguish local StoreKit testing from sandbox server verification. Exercise success, user cancel, pending approval, network loss after purchase, restart before acknowledgement, restore/reinstall, duplicate notification, renewal, expiration, refund/revocation and account switch. Prove one purchase grants once and invalid evidence grants nothing.

Return the state mapping, verification/fulfillment boundary, SDK/version, sandbox evidence and untested lifecycle cases. If store credentials or a backend are missing, produce fixtures/scaffolding and label live verification blocked rather than claiming purchases work.
