import os
import discord
from dotenv import load_dotenv
load_dotenv()
GUILD_ID=1554830636454514708
class C(discord.Client):
 async def on_ready(self):
  g=self.get_guild(GUILD_ID); cat=discord.utils.get(g.categories,name='╭・𝗕𝗢𝗧・𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦')
  for c in sorted(cat.text_channels,key=lambda x:x.position):
   count=0
   async for _ in c.history(limit=20): count+=1
   print(c.id, repr(c.name), 'recent<=20:', count)
  await self.close()
intents=discord.Intents.default()
C(intents=intents).run(os.getenv('DISCORD_TOKEN'))
