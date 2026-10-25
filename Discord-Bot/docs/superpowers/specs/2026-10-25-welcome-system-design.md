# RupZha Welcome System Design

## Intent
Make every new RupZha member immediately know they are welcomed, how to start, and where to choose game roles. Reuse the existing RupZha bot rather than adding another dependency.

## Goals
- Keep automatic `Member` role assignment.
- Post one polished welcome embed in `・𝗪𝗲𝗹𝗰𝗼𝗺𝗲` when a member joins.
- Mention the joining member, show the current member count, and give three clear next steps: rules, game roles, community.
- Keep the existing static welcome guide intact.
- Fail safely if the welcome channel or a referenced channel is unavailable.

## Non-goals
- No DM welcome messages.
- No additional Discord bot.
- No automatic game-role assignment.
- No changes to the strict role-access policy.

## Anti-goals
- Do not spam the welcome channel on bot restart.
- Do not expose secrets or require new credentials.
- Do not replace the existing onboarding flow with a generic third-party bot.

## Approaches
1. **Native RupZha welcome system (selected):** extend `on_member_join` in `bot.py` with a Discord embed. Best fit because the existing bot already owns onboarding and the welcome channel; no extra dependency or synchronization problem.
2. **Dedicated welcome bot:** adds a separate bot/dependency and duplicates onboarding responsibility. Rejected because it increases operational complexity without adding value here.
3. **Plain text join message:** simplest, but does not provide the premium, structured onboarding experience requested. Rejected in favor of an embed.

## Design
The join handler first attempts the existing `Member` role assignment, then sends a single embed to the configured welcome channel. The embed uses the member mention, display name, guild member count, and links to the existing rules, role-selection, and community entry points. Channel references are resolved from `PUBLIC_CHANNELS`, so renaming those configured channels remains localized.

The implementation will expose a small pure helper for constructing the welcome embed so it can be tested without a live Discord event. The live handler remains responsible for sending it and handling Discord API failures.

## Constraints
- Python + discord.py already used by the project.
- Keep the current channel names and strict role policy unchanged.
- Use the existing `.venv` runtime for verification.
