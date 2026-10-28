# Legacy repair scripts

These files are historical, one-time server repair/rebuild tools. They are intentionally kept out of the project root so normal deployment/startup cannot accidentally execute them.

## Rules
- Do not run these against production without reviewing the script and taking a server backup.
- The active bot entrypoint is `bot.py`.
- Verification/audit scripts remain in the project root because they are read-only or deployment checks.
- Never put a Discord token in these scripts or commit `.env` files.
