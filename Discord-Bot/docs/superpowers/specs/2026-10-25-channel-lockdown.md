# RupZha Channel Lockdown Design

## Goal
Tighten child-channel permissions without changing the existing strict category model.

## Rules
- Public onboarding/documentation channels are visible to everyone but read-only for members.
- Staff can post in locked public documentation channels.
- Client project status is visible to clients and staff but client-posting is disabled.
- Operations logs remain private.
- Wick, Ticket Tool, Statbot, Arcane, Xenon, and Carl-bot receive explicit write access only to their required log/dashboard channels.
- Native Discord Community Onboarding remains the only pre-join onboarding flow.
- No staff/client permissions are granted through onboarding.

## Protected channels
Welcome, Rules, Announcements, Choose Roles, How It Works, FAQ, Project Status, Logs, Wick Security Logs, Wick AntiRaid Logs, Ticket Panel, Statbot dashboards, Arcane Level Ups, Xenon Backups, and Carl-bot Logs.

## Non-goals
- Do not reset or recreate the server.
- Do not change the existing role hierarchy.
- Do not expose private business/team channels to normal members.
