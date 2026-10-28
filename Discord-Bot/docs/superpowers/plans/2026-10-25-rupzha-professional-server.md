# Rupzha Professional Discord Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Turn the existing Rupzha Discord into a polished gaming-community + professional client/agency server without deleting useful existing channels or permissions.

**Architecture:** Repair the live guild in place, using conservative renames and category/channel reconciliation. Update `bot.py` so its reconciliation logic understands legacy names and does not create duplicate categories/channels on future startups. Keep public gaming/community areas visually consistent and keep client/team/operations/tools areas private.

**Tech Stack:** Python 3, discord.py, dotenv, Discord API, existing Rupzha bot.

**Spec:** Existing Rupzha server design agreed in chat: premium/minimal aesthetic, `╭・𝗖𝗔𝗧𝗘𝗚𝗢𝗥𝗬` categories and `・𝗖𝗵𝗮𝗻𝗻𝗲𝗹` channels, gaming-first public area, professional client/staff/business areas, preserve existing permissions and purpose.

## Global Constraints

- Do not expose or rewrite the Discord token.
- Do not delete existing channels during cleanup.
- Preserve channel purpose and existing permission intent.
- Avoid burst PATCH requests; honor Discord 429 Retry-After responses.
- Use one consistent naming system instead of emoji-heavy names.
- Verify the live guild after every cleanup batch and before claiming completion.

## Review Focus

- Legacy/hyphenated names must map to the intended channel instead of causing duplicates.
- Blank `・` channels must receive the missing purpose/name rather than being deleted.
- Duplicate categories must be repurposed safely, not create another copy on bot restart.
- Game-specific visibility must continue to follow game roles.
- Private client/team/operations/tools categories must remain private.

---

### Task 1: Harden reconciliation logic

**Files:**
- Modify: `bot.py`
- Test: `tests/test_channel_naming.py`

- [ ] Add tests for normalized matching between styled names, ASCII hyphen variants, and legacy names.
- [ ] Run the focused tests and confirm the new matching behavior is initially absent/failing where applicable.
- [ ] Update `get_category`, `get_text`, and `get_voice` to reuse legacy/normalized matches before creating anything.
- [ ] Add explicit legacy-name aliases for the current broken server names.
- [ ] Compile and run focused tests.

### Task 2: Define the final server map

**Files:**
- Modify: `bot.py`

- [ ] Keep the existing public categories and game hubs.
- [ ] Repurpose duplicate categories into useful professional areas: Media & Content, Staff Tools, Event Voice, and BGMI/PUBG.
- [ ] Assign every currently blank channel a concrete purpose.
- [ ] Keep the visual grammar `╭・CATEGORY` / `・CHANNEL`.
- [ ] Update seeded copy so it references the final channel names.

### Task 3: Repair the live guild safely

**Files:**
- Create/modify: `rupzha_setup.py` if needed for one-time repair

- [ ] Snapshot current guild structure before edits.
- [ ] Apply category/channel renames in small sequential batches.
- [ ] Handle 429 Retry-After dynamically rather than retrying immediately.
- [ ] Verify there are no blank channel names, no accidental duplicate game categories, and no missing final categories.
- [ ] Verify permissions on private categories remain private.

### Task 4: Bot startup verification

**Files:**
- Modify: `bot.py` only as required by verification

- [ ] Start the bot once after the live repair.
- [ ] Confirm it connects to Rupzha and does not create duplicate categories/channels.
- [ ] Confirm onboarding role panel and existing bot workflows still initialize.
- [ ] Stop/restart once if needed to prove reconciliation is idempotent.
- [ ] Run `py_compile` and all focused tests.
