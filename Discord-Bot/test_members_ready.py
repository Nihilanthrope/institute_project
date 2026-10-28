import discord
from dotenv import dotenv_values
cfg=dotenv_values('.env')
i=discord.Intents.default(); i.guilds=True; i.members=True
class C(discord.Client):
 async def on_ready(self):
  print('READY_WITH_MEMBERS',[(g.id,g.name) for g in self.guilds])
  await self.close()
C(intents=i,guild_ready_timeout=5.0,chunk_guilds_at_startup=False,member_cache_flags=discord.MemberCacheFlags.none()).run(cfg['DISCORD_TOKEN'])
