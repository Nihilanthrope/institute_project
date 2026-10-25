# RupZha Role Governance Design

## Goal
Make role power intentional, remove unexplained native moderation power, standardize role colors, and keep optional roles unassigned until a member has a reason to receive them.

## Decisions
- Only Founder, Co-Founder, Administrator retain Discord Administrator permission.
- Operations keeps explicit operational moderation/channel permissions.
- Manager gets message/thread/audit-log powers but no native kick/ban.
- Moderator gets message/thread/moderation/timeout/kick powers but no ban.
- Support gets ticket/thread support only.
- Community, game, interest, notification, client, and team identity roles get no dangerous base permissions.
- Unrecognized custom roles are audited; they are not silently granted staff power.
- Existing managed integration/bot roles are not edited.
- Role colors are grouped: leadership, operations/moderation, team, client/community, games/interests, notifications.
- Add only purposeful optional roles: Trial Moderator, Event Host, QA / Tester, Partner, Community Helper. They are created unassigned with no permissions until an explicit workflow assigns them.
- Do not automatically assign optional roles.
- Existing Discord Community Onboarding remains the assignment path for member-selected roles.

## Non-goals
- Do not delete existing channels, roles, members, or integrations.
- Do not reset onboarding.
- Do not push or merge.
