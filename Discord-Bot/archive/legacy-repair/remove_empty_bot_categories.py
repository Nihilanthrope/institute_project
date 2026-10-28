import os
import discord
from dotenv import load_dotenv

load_dotenv("/home/nihilanthrope/github/Discord-Bot/.env")
GUILD_ID = 1554830636454514708
EMPTY_CATEGORIES = [
    "╭・𝗪𝗜𝗖𝗞", "╭・𝗧𝗜𝗖𝗞𝗘𝗧・𝗧𝗢𝗢𝗟", "╭・𝗦𝗧𝗔𝗧𝗕𝗢𝗧",
    "╭・𝗔𝗥𝗖𝗔𝗡𝗘", "╭・𝗫𝗘𝗡𝗢𝗡", "╭・𝗖𝗔𝗥𝗟・𝗕𝗢𝗧",
]
client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    try:
        guild = client.get_guild(GUILD_ID)
        if not guild:
            print("FAIL guild missing")
            return
        await guild.fetch_channels()
        for name in EMPTY_CATEGORIES:
            category = discord.utils.get(guild.categories, name=name)
            if category is None:
                print("ALREADY ABSENT", name)
                continue
            if category.channels:
                print("PRESERVED NONEMPTY", name, [c.name for c in category.channels])
                continue
            await category.delete(reason="Remove empty shell after bot-log category consolidation")
            print("DELETED VERIFIED EMPTY CATEGORY", name)
        await guild.fetch_channels()
        print("FINAL STRUCTURE", len(guild.channels), "guild channels,", len(guild.categories), "categories")
    finally:
        await client.close()

client.run(os.getenv("DISCORD_TOKEN"))
