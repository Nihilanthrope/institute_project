import asyncio
import discord
from dotenv import dotenv_values

cfg=dotenv_values('.env')
GUILD_ID=1554830636454514708

FIXES={
 1563875026195710052: ("╭・𝗩𝗔𝗟𝗢𝗥𝗔𝗡𝗧", {"voice":["・𝗩𝗮𝗹𝗼𝗿𝗮𝗻𝘁 𝗦𝗾𝘂𝗮𝗱"],"text":["・𝗖𝗵𝗮𝘁","・𝗟𝗙𝗚","・𝗖𝗹𝗶𝗽𝘀"]}),
 1563875054373044224: ("╭・𝗠𝗜𝗡𝗘𝗖𝗥𝗔𝗙𝗧", {"voice":["・𝗠𝗶𝗻𝗲𝗰𝗿𝗮𝗳𝘁"],"text":["・𝗖𝗵𝗮𝘁","・𝗟𝗙𝗚","・𝗕𝘂𝗶𝗹𝗱𝘀"]}),
 1563875085796774069: ("╭・𝗚𝗧𝗔 𝗩", {"voice":["・𝗚𝗧𝗔 𝗦𝗾𝘂𝗮𝗱"],"text":["・𝗖𝗵𝗮𝘁","・𝗟𝗙𝗚","・𝗖𝗹𝗶𝗽𝘀"]}),
 1563875119078834266: ("╭・𝗖𝗦𝟮", {"voice":["・𝗖𝗦𝟮 𝗦𝗾𝘂𝗮𝗱"],"text":["・𝗖𝗵𝗮𝘁","・𝗟𝗙𝗚","・𝗖𝗹𝗶𝗽𝘀"]}),
 1563875149357514894: ("╭・𝗙𝗢𝗥𝗧𝗡𝗜𝗧𝗘", {"voice":["・𝗙𝗼𝗿𝘁𝗻𝗶𝘁𝗲 𝗦𝗾𝘂𝗮𝗱"],"text":["・𝗖𝗵𝗮𝘁","・𝗟𝗙𝗚","・𝗖𝗹𝗶𝗽𝘀"]}),
 1563875179849977866: ("╭・𝗥𝗢𝗕𝗟𝗢𝗫", {"voice":["・𝗥𝗼𝗯𝗹𝗼𝘅"],"text":["・𝗖𝗵𝗮𝘁","・𝗟𝗙𝗚","・𝗚𝗮𝗺𝗲𝘀"]}),
 1563875217892315140: ("╭・𝗔𝗠𝗢𝗡𝗚 𝗨𝗦", {"voice":["・𝗔𝗺𝗼𝗻𝗴 𝗨𝘀 𝗟𝗼𝗯𝗯𝘆"],"text":["・𝗖𝗵𝗮𝘁","・𝗟𝗙𝗚","・𝗚𝗮𝗺𝗲𝘀"]}),
 1563875251748601978: ("╭・𝗔𝗣𝗘𝗫 𝗟𝗘𝗚𝗘𝗡𝗗𝗦", {"voice":["・𝗔𝗽𝗲𝘅 𝗦𝗾𝘂𝗮𝗱"],"text":["・𝗖𝗵𝗮𝘁","・𝗟𝗙𝗚","・𝗖𝗹𝗶𝗽𝘀"]}),
 1563875285068414996: ("╭・𝗕𝗚𝗠𝗜 • 𝗣𝗨𝗕𝗚", {"voice":["・𝗕𝗚𝗠𝗜 / 𝗣𝗨𝗕𝗚 𝗦𝗾𝘂𝗮𝗱"],"text":["・𝗖𝗵𝗮𝘁","・𝗟𝗙𝗚","・𝗖𝗹𝗶𝗽𝘀"]}),
 1563875314319360101: ("╭・𝗢𝗧𝗛𝗘𝗥 𝗚𝗔𝗠𝗘𝗦", {"voice":["・𝗢𝘁𝗵𝗲𝗿 𝗚𝗮𝗺𝗲𝘀"],"text":["・𝗖𝗵𝗮𝘁","・𝗟𝗙𝗚","・𝗚𝗮𝗺𝗲・𝗥𝗲𝗰𝗼𝗺𝗺𝗲𝗻𝗱𝗮𝘁𝗶𝗼𝗻𝘀"]}),
 1563875427951575071: ("╭・𝗘𝗩𝗘𝗡𝗧 𝗩𝗢𝗜𝗖𝗘", {"voice":["・𝗘𝘃𝗲𝗻𝘁 𝗟𝗼𝘂𝗻𝗴𝗲","・𝗚𝗮𝗺𝗲 𝗡𝗶𝗴𝗵𝘁","・𝗧𝗼𝘂𝗿𝗻𝗮𝗺𝗲𝗻𝘁 𝗥𝗼𝗼𝗺","・𝗖𝗵𝗶𝗹𝗹 𝗥𝗼𝗼𝗺","・𝗘𝘃𝗲𝗻𝘁 𝗔𝗙𝗞"],"text":[]}),
}

ORDER=[1563867987130323044,1563867989298642944,1563875014309052540,1563875026195710052,1563875054373044224,1563875085796774069,1563875119078834266,1563875149357514894,1563875179849977866,1563875217892315140,1563875251748601978,1563875285068414996,1563875314319360101,1563868179724374036,1563875427951575071,1563867991504855051,1563867993820241960,1563867996013985863,1563867999864234026,1563875023826194513]

class C(discord.Client):
 async def on_ready(self):
  g=self.get_guild(GUILD_ID)
  for cid,(catname,groups) in FIXES.items():
   c=g.get_channel(cid)
   if not c: continue
   if c.name!=catname:
    print('CATEGORY',c.name,'->',catname); await asyncio.sleep(1); await c.edit(name=catname,reason='Rupzha professional cleanup')
   for kind,names in groups.items():
    children=[x for x in c.channels if (x.type.value==2 if kind=='voice' else x.type.value==0)]
    children=sorted(children,key=lambda x:x.position)
    for child,new in zip(children,names):
     if child.name!=new:
      print('CHANNEL',child.name,'->',new); await asyncio.sleep(1); await child.edit(name=new,reason='Rupzha professional cleanup')
  # Use discord.py's bulk channel-position endpoint for a single ordered pass.
  mapping={g.get_channel(cid):i for i,cid in enumerate(ORDER)}
  mapping={c:p for c,p in mapping.items() if c}
  if hasattr(g,'edit_channel_positions'):
   print('REORDERING',len(mapping),'categories')
   await g.edit_channel_positions(positions=mapping,reason='Rupzha professional layout')
  await asyncio.sleep(2)
  await g.fetch_channels()
  cats=sorted(g.categories,key=lambda x:x.position)
  print('FINAL ORDER')
  for c in cats: print(c.position,c.name)
  await self.close()
C(intents=discord.Intents.default()).run(cfg['DISCORD_TOKEN'])
