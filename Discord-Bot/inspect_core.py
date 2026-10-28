import discord
from dotenv import dotenv_values
cfg=dotenv_values('.env')
IDS={1563867987130323044,1563867989298642944,1563867991504855051,1563867993820241960,1563867996013985863,1563867999864234026,1563868179724374036,1563875023826194513,1563875427951575071}
class C(discord.Client):
 async def on_ready(self):
  g=self.get_guild(1554830636454514708)
  for c in sorted(g.categories,key=lambda x:x.position):
   if c.id in IDS:
    print('\nCAT',c.id,c.position,c.name)
    for x in sorted(c.channels,key=lambda x:x.position): print(x.id,x.type,x.position,x.name)
  await self.close()
C(intents=discord.Intents.default()).run(cfg['DISCORD_TOKEN'])
