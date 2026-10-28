# RupZha Strict Role & Access Design

## Intent
Make RupZha's roles strict and predictable: permissions represent power, while category overwrites represent access. Ordinary roles never receive administrative capabilities merely to see a channel.

## Goals
- Give every functional role a precise responsibility.
- Keep dangerous Discord permissions limited to the smallest necessary staff set.
- Make private categories inaccessible to @everyone by default.
- Make game roles unlock only their matching game hub.
- Give bot-management areas only to staff who need them.
- Keep the configuration persistent through bot restarts.

## Non-goals
- Deleting/rebuilding the server again.
- Reordering managed integration roles.
- Granting `Manage Roles` to human staff by default.
- Giving clients or community members moderation powers.

## Anti-goals
- Broad "staff can see everything" access.
- Giving Developer/Designer/Content Creator destructive server permissions.
- Giving game roles any moderation or management permission.

## Approaches
1. **Category-first strict access (chosen):** role permissions stay minimal; category/channel overwrites define visibility. This is safest and scales cleanly.
2. Broad staff permissions: simpler initially but creates excessive privilege and makes future access changes risky.
3. Per-channel manual permissions: maximum granularity but too brittle for a 100+ channel server.

## Role policy
- Founder, Co-Founder, Administrator: Administrator.
- Operations: Manage Guild, Manage Channels, Manage Messages, View Audit Log, Kick, Ban.
- Manager: Manage Messages, Manage Threads, View Audit Log.
- Moderator: Manage Messages, Manage Threads, Moderate Members, Kick.
- Support: Manage Threads only.
- Developer, Designer, Content Creator, Client, Verified, Member, and all game roles: no elevated permissions.

## Access policy
- Public community: normal community roles.
- Game hubs: matching game role plus management/moderation staff.
- Client Hub: Client plus management/support staff; private project/ticket channels can be added later.
- Team HQ: Developer/Designer/Content Creator plus management.
- Operations: Operations and above.
- Apps & Tools: Operations/management staff.
- Wick: Moderator and above.
- Ticket Tool: Support and above.
- Statbot: Manager and above.
- Arcane: public level-up surface; configuration access restricted to management.
- Xenon: Founder/Co-Founder/Administrator only.
- Carl-bot: Moderator and above.

## Constraints
- Use existing `discord.py` project and guild.
- Never expose `.env` or the Discord token.
- Bot can only manage roles below its own role.
- Existing server structure remains intact.
