import os, asyncio, discord
from dotenv import load_dotenv
load_dotenv()
TOKEN=os.getenv('DISCORD_TOKEN') or os.getenv('TOKEN')
GUILD_ID=1554830636454514708
if not TOKEN: raise RuntimeError('DISCORD_TOKEN/TOKEN missing')
intents=discord.Intents.default(); intents.guilds=True
client=discord.Client(intents=intents)
ROLE_NAMES=['Founder','Co-Founder','Administrator','Operations','Manager','Moderator','Support','Developer','Designer','Content Creator','Client','Verified','Member','Valorant','Minecraft','GTA V','CS2','Fortnite','Roblox','Among Us','Apex Legends','BGMI / PUBG','Other Games']
PUBLIC=[
('╭・𝗦𝗧𝗔𝗥𝗧 𝗛𝗘𝗥𝗘',['・𝗪𝗲𝗹𝗰𝗼𝗺𝗲','・𝗥𝘂𝗹𝗲𝘀','・𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁𝘀','・𝗖𝗵𝗼𝗼𝘀𝗲・𝗥𝗼𝗹𝗲𝘀','・𝗛𝗼𝘄・𝗜𝘁・𝗪𝗼𝗿𝗸𝘀','・𝗙𝗔𝗤']),
('╭・𝗖𝗢𝗠𝗠𝗨𝗡𝗜𝗧𝗬',['・𝗚𝗲𝗻𝗲𝗿𝗮𝗹','・𝗚𝗮𝗺𝗶𝗻𝗴・𝗖𝗵𝗮𝘁','・𝗖𝗹𝗶𝗽𝘀・𝗛𝗶𝗴𝗵𝗹𝗶𝗴𝗵𝘁𝘀','・𝗠𝗲𝗺𝗲𝘀','・𝗦𝗰𝗿𝗲𝗲𝗻𝘀𝗵𝗼𝘁𝘀','・𝗟𝗙𝗚','・𝗦𝗵𝗼𝘄𝗰𝗮𝘀𝗲','・𝗖𝗼𝗻𝘁𝗮𝗰𝘁']),
('╭・𝗘𝗩𝗘𝗡𝗧𝗦',['・𝗘𝘃𝗲𝗻𝘁𝘀','・𝗚𝗶𝘃𝗲𝗮𝘄𝗮𝘆𝘀','・𝗧𝗼𝘂𝗿𝗻𝗮𝗺𝗲𝗻𝘁𝘀']),
('╭・𝗩𝗢𝗜𝗖𝗘',['・𝗥𝘂𝗽𝘇𝗵𝗮・𝗟𝗼𝘂𝗻𝗴𝗲','・𝗚𝗮𝗺𝗲・𝗡𝗶𝗴𝗵𝘁','・𝗖𝗵𝗶𝗹𝗹','・𝗔𝗙𝗞'])]
GAMES=['Valorant','Minecraft','GTA V','CS2','Fortnite','Roblox','Among Us','Apex Legends','BGMI / PUBG','Other Games']
PRIVATE={'╭・𝗖𝗟𝗜𝗘𝗡𝗧 𝗛𝗨𝗕':['・𝗖𝗹𝗶𝗲𝗻𝘁・𝗛𝗲𝗹𝗽','・𝗣𝗿𝗼𝗷𝗲𝗰𝘁・𝗥𝗲𝗾𝘂𝗲𝘀𝘁𝘀','・𝗣𝗿𝗼𝗷𝗲𝗰𝘁・𝗦𝘁𝗮𝘁𝘂𝘀','・𝗖𝗹𝗶𝗲𝗻𝘁・𝗙𝗲𝗲𝗱𝗯𝗮𝗰𝗸'],'╭・𝗧𝗘𝗔𝗠 𝗛𝗤':['・𝗧𝗲𝗮𝗺・𝗖𝗵𝗮𝘁','・𝗣𝗿𝗼𝗷𝗲𝗰𝘁𝘀','・𝗧𝗮𝘀𝗸𝘀','・𝗜𝗱𝗲𝗮𝘀','・𝗪𝗶𝗻𝘀'],'╭・𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦':['・𝗟𝗲𝗮𝗱𝘀','・𝗦𝗮𝗹𝗲𝘀','・𝗙𝗶𝗻𝗮𝗻𝗰𝗲','・𝗟𝗼𝗴𝘀','・𝗣𝗹𝗮𝗻𝗻𝗶𝗻𝗴'],'╭・𝗔𝗣𝗣𝗦 & 𝗧𝗢𝗢𝗟𝗦':['・𝗕𝗼𝘁・𝗖𝗼𝗻𝘁𝗿𝗼𝗹','・𝗜𝗻𝘁𝗲𝗴𝗿𝗮𝘁𝗶𝗼𝗻𝘀','・𝗔𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗼𝗻']}
@client.event
async def on_ready():
 g=client.get_guild(GUILD_ID)
 if not g: print('Guild not found'); return
 print(f'Connected: {g.name}')
 roles={r.name:r for r in g.roles}
 for name in ROLE_NAMES:
  if name not in roles:
   r=await g.create_role(name=name,reason='Rupzha clean rebuild'); roles[name]=r; await asyncio.sleep(.7); print('ROLE',name)
 staff=[roles[x] for x in ['Founder','Co-Founder','Administrator','Operations','Manager','Moderator','Support'] if x in roles]
 staff_over={g.default_role:discord.PermissionOverwrite(view_channel=False)}
 for r in staff: staff_over[r]=discord.PermissionOverwrite(view_channel=True,send_messages=True,read_message_history=True,connect=True,speak=True)
 async def cat(name,private=False):
  c=discord.utils.get(g.categories,name=name)
  if c:return c
  ow=staff_over if private else {}
  return await g.create_category(name,overwrites=ow,reason='Rupzha clean rebuild')
 async def text(cat,name):
  if discord.utils.get(cat.text_channels,name=name): return
  await g.create_text_channel(name,category=cat,reason='Rupzha clean rebuild'); await asyncio.sleep(.6)
 for name,chs in PUBLIC:
  c=await cat(name)
  for ch in chs: await text(c,ch)
 for game in GAMES:
  c=await cat(f'╭・𝗚𝗔𝗠𝗘・{game.upper()}')
  for ch in ['・𝗖𝗵𝗮𝘁','・𝗟𝗙𝗚','・𝗖𝗹𝗶𝗽𝘀']: await text(c,ch)
  if not discord.utils.get(c.voice_channels,name='・𝗚𝗮𝗺𝗲・𝗩𝗼𝗶𝗰𝗲'): await g.create_voice_channel('・𝗚𝗮𝗺𝗲・𝗩𝗼𝗶𝗰𝗲',category=c,reason='Rupzha clean rebuild')
 for name,chs in PRIVATE.items():
  c=await cat(name,True)
  for ch in chs: await text(c,ch)
 print('REBUILD COMPLETE',len(g.roles),'roles',len(g.channels),'channels')
 await client.close()
client.run(TOKEN)
