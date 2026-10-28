import os, discord
from dotenv import load_dotenv
load_dotenv()
TOKEN=os.getenv('DISCORD_TOKEN'); GID=1554830636454514708
intents=discord.Intents.default(); intents.members=True
bot=discord.Client(intents=intents)
@bot.event
async def on_ready():
 g=bot.get_guild(GID); me=g.me
 names=['Founder','Co-Founder','Administrator','Operations','Manager','Moderator','Support','Developer','Designer','Content Creator','Client','Verified','Member','Valorant','Minecraft','GTA V','CS2','Fortnite','Roblox','Among Us','Apex Legends','BGMI / PUBG','Other Games']
 print('GUILD',g.name,'ROLES',len(g.roles),'CHANNELS',len(g.channels),'CATEGORIES',len(g.categories))
 print('BOT_TOP',me.top_role.name,me.top_role.position)
 print('CUSTOM_POS',[(n,g.get_role(discord.utils.get(g.roles,name=n).id).position if discord.utils.get(g.roles,name=n) else None) for n in names])
 print('PRIVATE',[(c.name, c.overwrites_for(g.default_role).view_channel) for c in g.categories if c.name in ['╭・𝗖𝗟𝗜𝗘𝗡𝗧 𝗛𝗨𝗕','╭・𝗧𝗘𝗔𝗠 𝗛𝗤','╭・𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦','╭・𝗔𝗣𝗣𝗦 & 𝗧𝗢𝗢𝗟𝗦']])
 start=discord.utils.get(g.categories,name='╭・𝗦𝗧𝗔𝗥𝗧 𝗛𝗘𝗥𝗘')
 if start:
  for c in start.text_channels:
   count=0
   async for m in c.history(limit=20):
    if m.author==bot.user: count+=1
   print('START',c.name,'BOT_MESSAGES',count)
 await bot.close()
bot.run(TOKEN)
