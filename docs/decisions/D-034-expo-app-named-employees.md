---
id: D-034
title: "Mobile-first Expo app with named AI employees; a JSON API replaces the trader dashboard"
status: accepted
date: 2026-11-22
---

# D-034 — Mobile-first Expo app with named AI employees; a JSON API replaces the trader dashboard

- **Date:** 2026-11-22
- **Status:** accepted
- **Reversible?** costly. The app is weeks of work. The backend and the API contract survive a
  change of front end.

## Context

D-014 put the dashboard inside the API as server-rendered pages. The current `/dashboard` is one
page with no login and no JSON API. It suits an operator. It does not suit a trader on a phone.

The founder wants a polished, simple, mobile-first product that makes a sole trader feel they
have a team ("they are not doing this alone"). Dad dislikes business apps, so simplicity is the
test. Mockups: [v2](../design/mockups/v2/index.html). Competitor tools are form-based and
priced per feature ([competitors](../product/competitors.md), vendor pages only).

## Options considered

| Option | Outcome |
|---|---|
| **A** Expo (React Native, with a web build) | Chosen. One codebase for iOS, Android and web, with native camera and push notifications, which receipts and alerts need |
| B React web wrapped in Capacitor | A web view in a shell. Camera and push work, but feel less native, and it adds a second toolchain for little gain |
| C Server-rendered PWA (D-014's approach) | Stays Python-only. Cannot reach the polish or native camera and push the product depends on |

Costs of A: a second language (TypeScript) in a Python-first repo (D-007), a lint and type-check
step outside `just check`, and iOS builds need EAS cloud or a Mac. The founder is on Ubuntu.

## Decision

1. **`apps/mobile` is an Expo app** (TypeScript), with an iOS build later through EAS.
2. **The API grows a versioned JSON API** (`/v1`) with an OpenAPI schema, and a generated
   TypeScript client. Trader login is required. The mechanism is not decided here and needs its
   own record before the app ships. The existing `/dashboard` stays as an operator page.
   D-014 is superseded for the trader-facing UI only.
3. **Tab bar: Today · Jobs · (+) · Team · More.**
   - **Today:** at most three numbers, a "Needs you" list, and a "Watch" card.
   - **Jobs:** chips Leads · In work · Complete, with Lost behind an archive link (D-030).
   - **Team:** the AI employees, each a chat.
   - **More:** clients, settings, and how customer messages are sent (D-035).
4. **Three taps or fewer** for every key task:

   | Task | Path | Taps |
   |---|---|---|
   | Log a receipt | + → Snap → Confirm | 3 |
   | Add a note or photo to a job | + → Note → Save | 3 |
   | Approve a lead | Today → card → Approve | 3 |
   | See job spend against quote | Today → job | 2 |
   | Ask the team something | Team → person → type | 3 |
   | Read a customer's messages | Jobs → job → messages | 3 |

5. **+ is a shortcut, not a feature.** Every action on + also exists on the screen it belongs to:
   New job on Jobs, Add receipt on a job, Add note on a job, and a chat from Team. + never adds a
   capability. It only shortens the path. Reordering its options by context (receipt first when
   on a job, with the job already chosen) is allowed and is not required for the first release.
6. **AI employees are roles with names and avatars.** Roles are the unit: Receptionist (missed
   calls, leads, clarifying questions), Bookkeeper (receipts, spend against quote), and later
   Estimator. Names (Penny, Ruth, Ed) are placeholders and exist only in the trader's own chat.
   Anything a customer receives comes from the business, not from a named employee, and obeys
   D-004 and D-035.
7. **WhatsApp is a channel, not an agent** ([roadmap §5](../product/roadmap.md)). Twilio WhatsApp
   senders, with the sandbox for development. One number with a router, and each reply labelled
   with the employee ("Ruth · Bookkeeper"). Meta business verification is started early because
   it takes time.
8. **The design tokens** in the v2 mockups become the Expo theme file.

## Consequences

- A JSON API, trader auth and a generated client are prerequisites for the app. Channel-aware
  `send()` and a conversations table are prerequisites for chat.
- `just check` gains a mobile lint and type-check step.
- The mockups are synthetic. The three-tap table is checked against the built app, not assumed.
- Simplicity has to be defended screen by screen. The Today cap of three numbers is the guard
  against analytics creep.

## Source

Founder decisions, 2026-11-22; [mockups v2](../design/mockups/v2/index.html);
[competitors](../product/competitors.md); D-004, D-007, D-014.
