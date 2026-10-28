# Dedicated Bot Channels Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give OwO, Pokétwo, and Koya their own command channels so each of those bots can operate only in its own channel, while preserving the existing shared utility channel for other bots.

**Architecture:** Keep the existing bot-command category and permission helpers. Change only the three named member-facing bots from the shared channel to canonical dedicated channels, reconcile aliases/duplicates safely, and enforce bot-role overwrites so each named bot can read/send/use commands only in its own channel. The legacy shared channel remains for other utility bots.

**Tech Stack:** Python 3.14, discord.py 2.7.1, existing RupZha setup/reconciliation code, pytest.

**Spec:** Dedicated channels: `🤖・・𝗢𝘄𝗢`, `🎮・・𝗣𝗼𝗸𝗲𝘁𝘄𝗼`, `🌸・・𝗞𝗼𝘆𝗮`.

## Global Constraints

- Do not delete unrelated channels or categories.
- Preserve existing channel history where practical; do not blindly purge messages.
- OwO, Pokétwo, and Koya must not be able to send or use application commands in the other two dedicated channels.
- The shared utility channel remains available for other configured utility bots.
- Reconciliation must be idempotent: repeated bot restarts must not create duplicate channels.

## Review Focus

- Correct bot-to-channel mapping.
- No cross-bot command leakage.
- Duplicate/legacy channel handling.
- Restart idempotency.
- Existing tests and live startup behavior remain healthy.

## Tasks

- [ ] Add failing tests for dedicated mappings and cross-channel denial.
- [ ] Implement canonical dedicated-channel configuration and permission reconciliation.
- [ ] Add safe legacy/duplicate cleanup for the three bots only.
- [ ] Run targeted tests, then the full suite.
- [ ] Restart the live bot and verify the server state from logs/audit.
