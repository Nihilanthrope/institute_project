# RupZha Graphical Welcome Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Send a red-and-black animated RupZha welcome GIF with every new-member welcome message.

**Architecture:** Keep the existing `on_member_join` flow and `build_welcome_embed` API. Add a local generated GIF asset, attach it to the welcome message, and point the embed image at the attachment so Discord renders the graphic while preserving the existing text and channel lookup.

**Tech Stack:** Python, discord.py, Pillow, pytest.

**Spec:** User request: graphical red-and-black GIF welcome inside RupZha Discord.

## Global Constraints
- Do not rebuild or reset the live server.
- Preserve existing welcome channel lookup, onboarding, roles, and permissions.
- Do not log or expose the Discord token.
- Do not push or merge changes.
- The bot must continue to work when the asset exists locally in the project.

## Review Focus
- Emoji-prefixed welcome channel is still found.
- Missing rules/roles channels still produce a valid welcome.
- The GIF is actually attached to the Discord message.
- Repeated bot restarts do not create extra static panels.
- Existing test suite remains green.

---

### Task 1: Graphical welcome attachment

**Files:**
- Create: `assets/rupzha-welcome.gif`
- Modify: `bot.py`
- Test: `tests/test_welcome_system.py`

- [ ] Write failing test for the embed attachment URL.
- [ ] Run the focused test and verify the expected failure.
- [ ] Add the GIF asset and attach it from `on_member_join`.
- [ ] Set the embed image to `attachment://rupzha-welcome.gif`.
- [ ] Run focused and full test suites.
- [ ] Restart the bot and verify live welcome channel discovery.
