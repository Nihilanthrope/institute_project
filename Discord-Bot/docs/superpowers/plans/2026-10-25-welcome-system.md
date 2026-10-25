# RupZha Welcome System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a polished native welcome embed to RupZha's existing join handler while preserving automatic Member assignment and the existing onboarding flow.

**Architecture:** Keep all Discord event handling in `bot.py`, with a small pure `build_welcome_embed(...)` helper for deterministic tests. The join event resolves existing configured channels, sends one embed, and catches Discord API failures without breaking onboarding.

**Tech Stack:** Python 3.14, discord.py, unittest, existing RupZha `.venv`.

**Spec:** `docs/superpowers/specs/2026-10-25-welcome-system-design.md`

## Global Constraints

- Reuse the existing RupZha bot; no new bot or credentials.
- Keep the current `PUBLIC_CHANNELS` names and strict role-access policy unchanged.
- Do not send DMs or assign game roles automatically.
- Preserve the existing static welcome guide.

## Review Focus

- Missing optional rules/roles channels: helper should still construct a usable welcome embed.
- Display names containing unusual Unicode: embed construction must remain valid.
- Guild member count unavailable/zero in a unit test: helper must still produce a valid embed.
- Discord send failures: join handler must not crash after a member joins.
- Restart behavior: welcome output must only be triggered by `on_member_join`, not `on_ready`.

---

### Task 1: Welcome Embed Helper and Join Handler

**Files:**
- Modify: `bot.py` around the existing `on_member_join` handler
- Create: `tests/test_welcome_system.py`

**Interfaces:**
- Produces `build_welcome_embed(member, rules_channel=None, roles_channel=None) -> discord.Embed` for tests and the join event.
- Consumes the existing `PUBLIC_CHANNELS` mapping and `on_member_join` event.

- [ ] **Step 1: Write the failing test**

Add tests asserting `build_welcome_embed` creates an embed titled `𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗨𝗣𝗭𝗛𝗔`, mentions the member, includes their display name and guild member count, and includes clear next-step references for rules and game roles when channels are supplied. Add a second test proving the embed remains usable when optional channel objects are absent.

- [ ] **Step 2: Run the focused test to verify it fails**

Run: `.venv/bin/python -m unittest tests.test_welcome_system -v`
Expected: FAIL because `build_welcome_embed` does not exist yet.

- [ ] **Step 3: Implement the minimal helper and handler**

Implement `build_welcome_embed(member, rules_channel=None, roles_channel=None)` in `bot.py` using a dark/premium gaming presentation. Include the member mention, display name, `member.guild.member_count`, and concise steps pointing to rules, game roles, and the community. Replace the current one-line welcome send in `on_member_join` with this embed send while preserving Member-role assignment and existing error handling.

- [ ] **Step 4: Run the focused test to verify it passes**

Run: `.venv/bin/python -m unittest tests.test_welcome_system -v`
Expected: PASS with 2 tests.

- [ ] **Step 5: Run syntax verification**

Run: `.venv/bin/python -m py_compile bot.py tests/test_welcome_system.py`
Expected: exit 0 with no output.

- [ ] **Step 6: Commit**

```bash
git add bot.py tests/test_welcome_system.py docs/superpowers/specs/2026-10-25-welcome-system-design.md docs/superpowers/plans/2026-10-25-welcome-system.md
git commit -m "feat: add polished RupZha welcome system"
```
