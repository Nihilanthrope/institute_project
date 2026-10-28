# Red/Black Welcome Background Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

## Goal
Make RupZha's welcome system visibly match the requested Discord design: a clean animated red/black GIF used only as the embed background, the joining member's normal Discord avatar as the embed thumbnail, and one clean persistent welcome board without stale duplicate bot panels.

## Files
- `bot.py`: welcome embed detection/cleanup and member-join behavior.
- `assets/rupzha-welcome.gif`: replace the baked-avatar welcome artwork with a background-only animated asset.
- `tests/test_welcome_system.py`: tests for the background-only animated asset and stale-panel classification.

## Tasks
- [ ] Add failing tests for animated multi-frame background asset and stale static-panel detection.
- [ ] Run focused tests and confirm the new tests fail.
- [ ] Generate the red/black animated background GIF with no member/avatar/text baked into frames.
- [ ] Implement stale welcome-panel cleanup while preserving personalized join messages.
- [ ] Run focused and full test suites.
- [ ] Restart the live bot and clean the existing welcome channel's stale bot-generated static panels, then publish exactly one persistent panel.
- [ ] Verify the live channel contains the new background asset and that the member-join embed still uses the normal avatar thumbnail.
