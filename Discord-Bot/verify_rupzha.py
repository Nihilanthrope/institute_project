import discord
from dotenv import dotenv_values
cfg=dotenv_values('.env')
EXPECTED={
'╭・𝗦𝗧𝗔𝗥𝗧 𝗛𝗘𝗥𝗘','╭・𝗖𝗢𝗠𝗠𝗨𝗡𝗜𝗧𝗬','╭・𝗠𝗘𝗗𝗜𝗔 & 𝗖𝗢𝗡𝗧𝗘𝗡𝗧','╭・𝗖𝗟𝗜𝗘𝗡𝗧 𝗛𝗨𝗕','╭・𝗧𝗘𝗔𝗠 𝗛𝗤','╭・𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦','╭・𝗔𝗣𝗣𝗦 & 𝗧𝗢𝗢𝗟𝗦','╭・𝗦𝗧𝗔𝗙𝗙 𝗧𝗢𝗢𝗟𝗦','╭・𝗖𝗢𝗠𝗠𝗨𝗡𝗜𝗧𝗬 𝗩𝗢𝗜𝗖𝗘','╭・𝗘𝗩𝗘𝗡𝗧 𝗩𝗢𝗜𝗖𝗘','╭・𝗩𝗔𝗟𝗢𝗥𝗔𝗡𝗧','╭・𝗠𝗜𝗡𝗘𝗖𝗥𝗔𝗙𝗧','╭・𝗚𝗧𝗔 𝗩','╭・𝗖𝗦𝟮','╭・𝗙𝗢𝗥𝗧𝗡𝗜𝗧𝗘','╭・𝗥𝗢𝗕𝗟𝗢𝗫','╭・𝗔𝗠𝗢𝗡𝗚 𝗨𝗦','╭・𝗔𝗣𝗘𝗫 𝗟𝗘𝗚𝗘𝗡𝗗𝗦','╭・𝗕𝗚𝗠𝗜 • 𝗣𝗨𝗕𝗚','╭・𝗢𝗧𝗛𝗘𝗥 𝗚𝗔𝗠𝗘𝗦'}
class C(discord.Client):
 async def on_ready(self):
  g=self.get_guild(1554830636454514708); cats={c.name:c for c in g.categories}
  print('CATEGORY_COUNT',len(cats))
  print('MISSING_CATEGORIES',sorted(EXPECTED-set(cats)))
  print('BLANK_CHANNELS',[(c.id,c.name) for c in g.channels if c.name in ('','・')])
  print('DUPLICATE_CATEGORY_NAMES',[n for n in cats if list(cats).count(n)>1])
  for n in ['╭・𝗩𝗔𝗟𝗢𝗥𝗔𝗡𝗧','╭・𝗠𝗜𝗡𝗘𝗖𝗥𝗔𝗙𝗧','╭・𝗚𝗧𝗔 𝗩','╭・𝗖𝗦𝟮','╭・𝗙𝗢𝗥𝗧𝗡𝗜𝗧𝗘','╭・𝗥𝗢𝗕𝗟𝗢𝗫','╭・𝗔𝗠𝗢𝗡𝗚 𝗨𝗦','╭・𝗔𝗣𝗘𝗫 𝗟𝗘𝗚𝗘𝗡𝗗𝗦','╭・𝗕𝗚𝗠𝗜 • 𝗣𝗨𝗕𝗚','╭・𝗢𝗧𝗛𝗘𝗥 𝗚𝗔𝗠𝗘𝗦']:
   c=cats.get(n); print(n,'TEXT',len(c.text_channels) if c else 0,'VOICE',len(c.voice_channels) if c else 0)
  for n in ['╭・𝗖𝗟𝗜𝗘𝗡𝗧 𝗛𝗨𝗕','╭・𝗧𝗘𝗔𝗠 𝗛𝗤','╭・𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦','╭・𝗔𝗣𝗣𝗦 & 𝗧𝗢𝗢𝗟𝗦']:
   c=cats.get(n); print(n,'everyone_view',c.overwrites_for(g.default_role).view_channel)
  await self.close()
C(intents=discord.Intents.default()).run(cfg['DISCORD_TOKEN'])
