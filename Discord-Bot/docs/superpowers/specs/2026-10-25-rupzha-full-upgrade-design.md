# RupZha Full Upgrade Design

## Intent
Turn the existing RupZha Discord server and Python bot into a polished, reliable gaming/community server with a real support system, moderation and security automation, member progression, community utilities, useful statistics, and a clean client/team workspace — without resetting or recreating the server.

## Current State
The server already has native Discord Community Onboarding, strict role/category access, protected documentation/log channels, game hubs, client/team/operations areas, and a 674-line discord.py bot. Existing work must be preserved.

## Goals
- Add a first-party ticket/support workflow with private ticket channels, categories, close/reopen, and transcript-ready structure.
- Add safe moderation and security automation: logging, anti-spam, raid/join protection, moderation commands, and staff alerts.
- Add member progression and community utilities: XP/levels, profiles, LFG, suggestions, polls, events, giveaways, and reminders where practical.
- Add durable SQLite-backed state so restarts do not lose member XP, moderation records, ticket metadata, or settings.
- Add staff/client operational commands without exposing private areas to normal members.
- Improve observability and diagnostics so live configuration regressions are obvious.
- Keep the current visual identity: dark, minimal, premium, selective Unicode styling.

## Non-goals / Anti-goals
- Never reset, rebuild, or recreate the server.
- Never grant normal members dangerous Discord permissions.
- Never expose client, team, operations, or security logs publicly.
- Never store the Discord token or other secrets in source code or database records.
- Do not add unnecessary dependencies when discord.py + Python standard library/SQLite are sufficient.
- Do not duplicate native Discord onboarding with another post-join onboarding wall.
- Do not create a giant monolithic command file if focused modules can be added safely.

## Constraints
- Existing server ID: 1554830636454514708.
- Existing Python bot uses discord.py 2.7.1 and Python 3.14.
- Existing strict role hierarchy and channel policies remain authoritative.
- Existing bot integrations remain in place; new features should coexist with Wick, Ticket Tool, Statbot, Arcane, Xenon, and Carl-bot.
- Existing modified files and prior tests must not be discarded.
- No automatic git push or merge.

## Recommended Architecture
Use the current bot as the entry point, but split new behavior into focused modules: configuration/policy, persistence, moderation/security, tickets, member progression, community utilities, and diagnostics. SQLite is the default persistence layer because the bot is a single-server Python service and needs durability without introducing a database service.

The upgrade is phased so each subsystem is independently testable and deployable:
1. Foundation + persistence + diagnostics.
2. Security/moderation/logging.
3. Ticket/support workflow.
4. Member XP/profiles and community utilities.
5. Client/team operations and polished UX.
6. Live verification and regression hardening.

## Success Criteria
A restart does not erase state; normal members cannot reach private areas; staff can safely moderate; members can open/close support tickets; XP/profile state survives restarts; community commands work without bypassing role policy; bot startup reports a clean audit; and the complete test suite passes before the upgraded bot is restarted live.

## Builder Decisions
- Use SQLite with one local database file under the project runtime directory, excluded from git.
- Use discord.py app commands and persistent views where Discord requires interactive controls.
- Prefer existing channels/categories over creating new ones; only create a missing channel when a feature genuinely needs it and its name is part of the design.
- Keep sensitive actions staff-gated both through Discord command default permissions and explicit runtime role checks.
- Use conservative anti-raid defaults to avoid false positives; destructive moderation remains staff-controlled.
