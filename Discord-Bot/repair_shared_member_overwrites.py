import asyncio
from pathlib import Path

import discord
from dotenv import dotenv_values

ROOT = Path(__file__).parent
TOKEN = dotenv_values(ROOT / ".env").get("DISCORD_TOKEN")
GUILD_ID = 1554830636454514708
PRIVATE = {"╭・𝗖𝗟𝗜𝗘𝗡𝗧 𝗛𝗨𝗕", "╭・𝗧𝗘𝗔𝗠 𝗛𝗤", "╭・𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦", "╭・𝗔𝗣𝗣𝗦 & 𝗧𝗢𝗢𝗟𝗦"}
SPECIAL = {
    "Wick": {"📋・・𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆・𝗟𝗼𝗴𝘀", "📋・・𝗔𝗻𝘁𝗶𝗥𝗮𝗶𝗱・𝗟𝗼𝗴𝘀"},
    "Ticket Tool": {"🎫・・𝗧𝗶𝗰𝗸𝗲𝘁・𝗣𝗮𝗻𝗲𝗹"},
    "Statbot": {"📊・・𝗦𝘁𝗮𝘁𝘀・𝗗𝗮𝘀𝗵𝗯𝗼𝗮𝗿𝗱", "📈・・𝗔𝗰𝘁𝗶𝘃𝗶𝘁𝘆・𝗦𝘁𝗮𝘁𝘀"},
    "Arcane": {"🏆・・𝗟𝗲𝘃𝗲𝗹・𝗨𝗽𝘀"},
    "Xenon": {"💾・・𝗕𝗮𝗰𝗸𝘂𝗽𝘀"},
    "Carl-bot": {"📋・・𝗖𝗮𝗿𝗹・𝗟𝗼𝗴𝘀"},
}

class Repair(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default() | discord.Intents.members)

    async def paced(self):
        await asyncio.sleep(1.25)

    async def on_ready(self):
        guild = self.get_guild(GUILD_ID)
        if not guild:
            print("GUILD NOT FOUND")
            await self.close(); return
        member_role = discord.utils.get(guild.roles, name="Member")
        if not member_role:
            print("MEMBER ROLE NOT FOUND")
            await self.close(); return

        # Remove the dangerous shared Member-role channel overwrites created by the
        # previous generic bot pass. This restores the role to normal inheritance.
        removed = 0
        for channel in guild.text_channels:
            if channel.overwrites_for(member_role) != discord.PermissionOverwrite():
                try:
                    await self.paced()
                    await channel.set_permissions(member_role, overwrite=None, reason="RupZha security repair: remove bot rules from shared Member role")
                    removed += 1
                except discord.HTTPException as exc:
                    print(f"WARN MEMBER CLEANUP #{channel.name}: {exc}")

        bots = [m for m in guild.members if m.bot and m.top_role.name == "Member"]
        applied = 0
        for member in bots:
            allowed = SPECIAL.get(member.name)
            if allowed is None:
                safe = "".join(ch for ch in member.name.lower() if ch.isalnum() or ch in "-_ ").strip().replace(" ", "-")
                allowed = {f"🤖・・{safe[:80] or str(member.id)}"}

            for category in guild.categories:
                private = category.name in PRIVATE
                desired = discord.PermissionOverwrite(
                    view_channel=not private,
                    read_message_history=not private,
                    send_messages=False,
                    send_messages_in_threads=False,
                    create_public_threads=False,
                    create_private_threads=False,
                    use_application_commands=False,
                    add_reactions=False,
                )
                try:
                    if category.overwrites_for(member) != desired:
                        await self.paced()
                        await category.set_permissions(member, overwrite=desired, reason="RupZha bot isolation: member-level category policy")
                        applied += 1
                except discord.HTTPException as exc:
                    print(f"WARN CATEGORY {member.name} {category.name}: {exc}")

            for channel in guild.text_channels:
                if channel.name not in allowed:
                    continue
                desired = discord.PermissionOverwrite(
                    view_channel=True,
                    read_message_history=True,
                    send_messages=True,
                    send_messages_in_threads=True,
                    create_public_threads=True,
                    create_private_threads=False,
                    use_application_commands=True,
                    add_reactions=True,
                    embed_links=True,
                    attach_files=True,
                )
                try:
                    if channel.overwrites_for(member) != desired:
                        await self.paced()
                        await channel.set_permissions(member, overwrite=desired, reason="RupZha bot isolation: dedicated command channel")
                        applied += 1
                except discord.HTTPException as exc:
                    print(f"WARN OWN CHANNEL {member.name} #{channel.name}: {exc}")

        print(f"MEMBER ROLE CLEANED {removed} channels")
        print(f"BOT MEMBER POLICIES APPLIED {applied} overwrites across {len(bots)} shared-role bots")
        await self.close()

if not TOKEN:
    raise SystemExit("DISCORD_TOKEN missing")
Repair().run(TOKEN)
