import os
import discord
from dotenv import load_dotenv

load_dotenv("/home/nihilanthrope/github/Discord-Bot/.env")
GUILD_ID = 1554830636454514708
NEW_CATEGORY = "╭・𝗕𝗢𝗧・𝗟𝗢𝗚𝗦"
STAFF = {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator", "Support"}
PRIVATE_MOVES = [
    ("📋・・𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆・𝗟𝗼𝗴𝘀", "╭・𝗪𝗜𝗖𝗞"),
    ("📋・・𝗔𝗻𝘁𝗶𝗥𝗮𝗶𝗱・𝗟𝗼𝗴𝘀", "╭・𝗪𝗜𝗖𝗞"),
    ("📊・・𝗦𝘁𝗮𝘁𝘀・𝗗𝗮𝘀𝗵𝗯𝗼𝗮𝗿𝗱", "╭・𝗦𝗧𝗔𝗧𝗕𝗢𝗧"),
    ("📈・・𝗔𝗰𝘁𝗶𝘃𝗶𝘁𝘆・𝗦𝘁𝗮𝘁𝘀", "╭・𝗦𝗧𝗔𝗧𝗕𝗢𝗧"),
    ("💾・・𝗕𝗮𝗰𝗸𝘂𝗽𝘀", "╭・𝗫𝗘𝗡𝗢𝗡"),
    ("📋・・𝗖𝗮𝗿𝗹・𝗟𝗼𝗴𝘀", "╭・𝗖𝗔𝗥𝗟・𝗕𝗢𝗧"),
]
PUBLIC_MOVES = {
    "🎫・・𝗧𝗶𝗰𝗸𝗲𝘁・𝗣𝗮𝗻𝗲𝗹": "╭・𝗦𝗧𝗔𝗥𝗧 𝗛𝗘𝗥𝗘",
    "🏆・・𝗟𝗲𝘃𝗲𝗹・𝗨𝗽𝘀": "╭・𝗘𝗩𝗘𝗡𝗧𝗦",
}
client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    try:
        guild = client.get_guild(GUILD_ID)
        if not guild:
            print("FAIL guild missing")
            return
        categories = {c.name: c for c in guild.categories}
        for old_name in {"╭・𝗪𝗜𝗖𝗞", "╭・𝗧𝗜𝗖𝗞𝗘𝗧・𝗧𝗢𝗢𝗟", "╭・𝗦𝗧𝗔𝗧𝗕𝗢𝗧", "╭・𝗔𝗥𝗖𝗔𝗡𝗘", "╭・𝗫𝗘𝗡𝗢𝗡", "╭・𝗖𝗔𝗥𝗟・𝗕𝗢𝗧"}:
            if old_name not in categories:
                print("FAIL missing expected category", old_name)
                return
        destination = categories.get(NEW_CATEGORY)
        if destination is None:
            overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
            for name in STAFF:
                role = discord.utils.get(guild.roles, name=name)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
            destination = await guild.create_category(
                NEW_CATEGORY, overwrites=overwrites,
                reason="Consolidate private bot integration logs without changing channel-level permissions",
            )
            print("CREATED", NEW_CATEGORY)

        moved = 0
        for position, (name, old_category_name) in enumerate(PRIVATE_MOVES):
            channel = discord.utils.get(guild.text_channels, name=name)
            if not channel:
                print("WARN missing private channel", name)
                continue
            if channel.category != destination:
                await channel.edit(
                    category=destination, position=position, sync_permissions=False,
                    reason="Consolidate private integration logs; preserve channel-level permissions",
                )
                print("MOVED PRIVATE", name, "from", old_category_name, "to", NEW_CATEGORY)
                moved += 1

        for name, target_name in PUBLIC_MOVES.items():
            channel = discord.utils.get(guild.text_channels, name=name)
            target = categories.get(target_name)
            if not channel or not target:
                print("WARN missing public move", name, target_name)
                continue
            if channel.category != target:
                position = max((c.position for c in target.channels), default=-1) + 1
                await channel.edit(
                    category=target, position=position, sync_permissions=False,
                    reason="Keep member-facing bot feature in a public category",
                )
                print("MOVED PUBLIC", name, "to", target_name)

        apps = categories.get("╭・𝗔𝗣𝗣𝗦 & 𝗧𝗢𝗢𝗟𝗦")
        if apps:
            await destination.edit(position=apps.position + 1, reason="Place private bot logs beside staff tools")
        await guild.fetch_channels()
        print("MOVE COMPLETE", "channels", len(guild.channels), "categories", len(guild.categories), "private_moved", moved)
        for name in [NEW_CATEGORY, "╭・𝗕𝗢𝗧・𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦", "╭・𝗦𝗧𝗔𝗥𝗧 𝗛𝗘𝗥𝗘", "╭・𝗘𝗩𝗘𝗡𝗧𝗦"]:
            cat = discord.utils.get(guild.categories, name=name)
            if cat:
                print("FINAL", cat.position, cat.name, [c.name for c in sorted(cat.channels, key=lambda c: c.position)])
    finally:
        await client.close()

client.run(os.getenv("DISCORD_TOKEN"))
