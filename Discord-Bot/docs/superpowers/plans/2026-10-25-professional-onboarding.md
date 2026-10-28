# Professional Rupzha Onboarding Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Turn the fresh Rupzha Discord into a professional, low-friction community/client server with safe self-service role selection and automatic joiner onboarding.

**Architecture:** Keep the existing idempotent server builder, add a small onboarding configuration module, and keep the Discord bot online after setup so member-join and button/select interactions continue working. Self-assignable roles are explicitly allowlisted; staff/business roles remain protected.

**Tech Stack:** Python, discord.py, python-dotenv, pytest.

**Spec:** User wants a complete professional server, with new joiners clearly guided to choose appropriate roles, without avoidable runtime errors.

## Global Constraints

- Never expose or log the Discord token.
- Never allow self-assignment of Founder/Admin/Lead/Team/Bot roles.
- Keep setup idempotent: rerunning the bot must not duplicate roles/channels or onboarding messages.
- Handle Discord permission/API failures per operation so one failure does not crash the whole setup.
- The bot must remain online after setup to process member joins and onboarding interactions.

## Review Focus

- Existing server rerun: no duplicate channels, roles, or onboarding panels.
- Member joins before onboarding roles exist: member still receives a usable welcome path.
- A user selects multiple business roles: protected roles cannot be selected.
- Interaction after bot restart: persistent custom IDs continue to work.
- Missing privileged member intent: bot reports the exact requirement instead of silently failing.

### Task 1: Onboarding configuration
**Files:** Create `onboarding_config.py`; Test `tests/test_onboarding_config.py`
- Define an explicit allowlist of self-assignable roles and polished labels/descriptions.
- Define the joiner-facing onboarding copy.
- Run the focused pytest test and require green.

### Task 2: Discord onboarding runtime
**Files:** Modify `bot.py`
- Enable member intent and persistent UI components.
- Add a dedicated role-selection channel under Start Here.
- Seed a single onboarding panel with buttons/select menu.
- Add `on_member_join` welcome handling and a safe default Member role.
- Implement role selection using the allowlist only, with clear ephemeral confirmations.
- Keep the bot running after setup.

### Task 3: Verification
**Files:** No new files
- Run pytest.
- Run Python compile check.
- Run the bot against the actual Rupzha guild and inspect startup/setup output.
- Confirm the process remains running after setup.
