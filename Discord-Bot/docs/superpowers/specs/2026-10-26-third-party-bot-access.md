# RupZha Third-Party Bot Access Design

## Goal
Make third-party Discord bots useful without letting them become noisy or leak into private server areas.

## Behavior
- Each utility bot has one dedicated public channel where it may send messages and use application commands.
- Utility bots may view/read message history in public/community channels so activity-driven features can work (for example Pokétwo spawning from chat activity).
- Utility bots may not send messages, create threads, or use application commands outside their own channel.
- Private staff/client/operations/tooling categories remain hidden from utility bots unless a bot is explicitly configured for that private integration channel.
- Existing dedicated integration channels (Wick, Ticket Tool, Statbot, Arcane, Xenon, carl-bot) keep their current purpose-specific write permissions.
- The policy is idempotent: restarting RupZha Bot reconciles drift without duplicating roles/channels.

## Current dedicated utility bots
- OwO -> 🤖・・𝗢𝘄𝗢
- Pokétwo -> 🎮・・𝗣𝗼𝗸𝗲𝘁𝘄𝗼
- Koya -> 🌸・・𝗞𝗼𝘆𝗮

## Non-goals
- Do not change human member permissions.
- Do not change integration-managed roles.
- Do not grant Administrator/Manage Server permissions.
- Do not expose private client/staff conversations merely to support chat activity features.

## Security rule
Read broadly where useful; write narrowly where required. A bot's dedicated channel is the only place it receives send/application-command capability from this policy.
