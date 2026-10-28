import discord
from dotenv import dotenv_values
cfg=dotenv_values('.env')
IDS={1563875026195710052,1563875054373044224,1563875085796774069,1563875119078834266,1563875149357514894,1563875179849977866,1563875217892315140,1563875251748601978,1563875285068414996,1563875314319360101,1563875014309052540}
class C(discord.Client):
 async def on_ready(self):
  g=self.get_guild(1554830636454514708)
  for c in sorted(g.categories,key=lambda x:x.position):
   if c.id in IDS:
    print('\nCAT',c.id,c.position,c.name)
    for x in sorted(c.channels,key=lambda x:x.position): print(x.id,x.type,x.position,x.name)
  await self.close()
C(intents=discord.Intents.default()).run(cfg['DISCORD_TOKEN'])
