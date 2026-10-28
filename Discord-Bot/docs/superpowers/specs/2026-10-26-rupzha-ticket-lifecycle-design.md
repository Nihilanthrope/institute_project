# Rupzha Ticket Lifecycle Design

## Intent
Turn the existing Rupzha ticket system into a complete agency-grade workflow: active ownership, staff controls, structured closure, transcript retention, feedback, automatic archival, and safe reopening.

## Goals
- Keep tickets private and permission-safe.
- Let staff claim, prioritize, escalate, add/remove users, and close/reopen tickets.
- On close, make the ticket read-only, preserve a transcript, show feedback, and schedule archival.
- Archive closed tickets in a private category for 24 hours before deletion.
- Cancel pending archival when a ticket is reopened or receives explicit activity.
- Persist lifecycle state in SQLite so bot restarts do not lose timers or ownership.
- Keep all important lifecycle actions auditable.

## Non-goals
- Replacing the existing SQLite storage layer.
- Rebuilding the server's category structure.
- Automatically changing third-party bot permissions.

## Anti-goals
- Do not delete active tickets.
- Do not expose archived/private ticket content to normal members.
- Do not rely only on in-memory timers.

## Approach
Use the current `bot.py` Discord UI and `tickets.py` service layer. Extend the ticket schema with lifecycle metadata and implement a periodic reconciliation task that handles due archival/deletion from persisted timestamps. Closed channels move to a private archive category and become read-only; a transcript is generated before the move. Staff controls are implemented with persistent Discord buttons/selects and guarded by existing staff checks.

## Defaults
- Archive delay: 24 hours after closure.
- Archived tickets remain private and are deleted when the persisted archive deadline is reached.
- Reopen is staff-only.
- Ticket opener may close their own ticket.
- New activity on an open ticket updates last activity; archived/closed channels do not silently reopen from arbitrary messages.

## Auditability
Persist claimed staff member, priority, escalation state, closure reason, transcript path, archive timestamp, and lifecycle timestamps. Important UI actions should also produce a staff-facing audit log message when the configured log channel exists.
