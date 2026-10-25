import os
import discord
from dotenv import load_dotenv
load_dotenv()
GUILD_ID = 1554830636454514708

class Audit(discord.Client):
    async def on_ready(self):
        g = self.get_guild(GUILD_ID)
        print(f"GUILD {g.name} channels={len(g.channels)} roles={len(g.roles)}")
        for cat in sorted(g.categories, key=lambda c: c.position):
            print(f"CAT {cat.position:02d} {cat.name}")
            for c in sorted(cat.channels, key=lambda c: c.position):
                kind = "VOICE" if isinstance(c, discord.VoiceChannel) else "TEXT"
                print(f"  {kind} {c.position:02d} {c.name} | {c.id}")
        print("BOT MEMBERS")
        for m in sorted((m for m in g.members if m.bot), key=lambda x: x.name.lower()):
            print(f"BOT {m.name} | top={m.top_role.name} | {m.id}")
        await self.close()

intents = discord.Intents.default()
intents.members = True
Audit(intents=intents).run(os.getenv("DISCORD_TOKEN"))
