import discord
from dotenv import dotenv_values
cfg=dotenv_values('.env')
class C(discord.Client):
    async def on_ready(self):
        print('READY', self.user, [(g.id,g.name) for g in self.guilds])
        await self.close()
C(intents=discord.Intents.default()).run(cfg['DISCORD_TOKEN'])
