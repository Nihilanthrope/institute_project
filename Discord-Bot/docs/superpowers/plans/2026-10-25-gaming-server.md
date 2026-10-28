# Rupzha Gaming Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn Rupzha Core into a gaming-first Discord server where onboarding choices assign game/interest/notification roles and those roles control which game-specific chats and voice rooms members can see.

**Architecture:** Keep the existing Python discord.py bot and its staff/private permission model. Add a structured gaming layer with self-assignable game, interest, and notification roles; create role-exclusive game categories/channels; and use persistent dropdowns in the onboarding channel to assign roles. The existing staff, client, operations, and tools areas remain private.

**Tech Stack:** Python 3, discord.py, python-dotenv, Discord role/category/channel permissions, persistent Discord UI select menus.

**Spec:** This plan implements the gaming-first Rupzha redesign requested in chat.

## Global Constraints

- Do not expose bot tokens or credentials.
- Self-service members must never be able to assign protected staff/client/security roles.
- Game channels are visible only to members with the corresponding game role, plus staff roles.
- Game choices may be changed later without accumulating stale game roles.
- Age selection is optional and uses ranges, not exact ages.
- Existing private staff/client/operations/tool areas remain protected.
- Verify syntax, configuration, role/channel creation, and bot startup before claiming completion.

## Review Focus

- A member selecting multiple games must receive all selected game roles and see all selected game hubs.
- Changing a game selection must remove old self-service game roles instead of accumulating them.
- Staff must retain access to game hubs regardless of game role.
- Protected roles such as Founder, Admin, Client, Partner, Prospect, VIP, Muted, and Quarantined must not be self-assignable.
- Bot restart must preserve interactive onboarding controls through persistent custom IDs.

### Task 1: Gaming role and channel model

**Files:**
- Modify: `onboarding_config.py`
- Modify: `bot.py`

**Interfaces:**
- `GAME_ROLES`, `AGE_ROLES`, `INTEREST_ROLES`, and `NOTIFICATION_ROLES` define self-service groups.
- `GAME_HUBS` defines each game category, text channels, and voice channels.
- `RoleSelectView` provides persistent onboarding controls.

- [ ] Add gaming roles for Valorant, Minecraft, GTA V, CS2, Fortnite, Roblox, Among Us, Apex Legends, BGMI/PUBG, and Other Games.
- [ ] Add optional age-range roles: 16–17, 18–20, 21–24, 25+.
- [ ] Separate self-service role groups so protected business/staff roles cannot be selected.
- [ ] Add game hub definitions and staff bypass roles.
- [ ] Keep the existing management/client/team permission model intact.

### Task 2: Interactive gaming onboarding

**Files:**
- Modify: `bot.py`
- Modify: `onboarding_config.py`

- [ ] Replace the single mixed-role dropdown with clear persistent sections for games, interests, notifications, and optional age range.
- [ ] Allow multiple games/interests/notifications.
- [ ] Allow exactly one age range, with a skip option.
- [ ] When a selection changes, remove stale roles from the same group and apply the new roles.
- [ ] Add a concise completion response showing what was assigned.
- [ ] Ensure protected roles can never be added through onboarding.

### Task 3: Gaming server layout and permissions

**Files:**
- Modify: `bot.py`

- [ ] Add public default channels for welcome, rules, general, gaming chat, clips, memes, screenshots, LFG, events, and giveaways.
- [ ] Create one role-exclusive category per major game with chat, LFG, clips/builds, and a voice room where appropriate.
- [ ] Grant the corresponding game role access to its hub.
- [ ] Grant Founder, Co-Founder, Administrator, Operations Manager, Head Moderator, Moderator, and Support appropriate bypass access.
- [ ] Keep Client Hub, Team HQ, Operations, and Apps & Tools private.
- [ ] Seed concise channel topics/messages so the server looks complete rather than empty.

### Task 4: Verification and startup

**Files:**
- No new files unless needed for verification.

- [ ] Run `python -m py_compile bot.py onboarding_config.py`.
- [ ] Run import/config assertions for all role and game definitions.
- [ ] Restart the bot cleanly.
- [ ] Verify the bot logs into Discord without exceptions.
- [ ] Verify expected roles and gaming channels exist and private categories remain protected.
- [ ] Verify the persistent onboarding view is registered after restart.
