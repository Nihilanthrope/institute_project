import os
import discord
from dotenv import load_dotenv
load_dotenv()
GUILD_ID = 1554830636454514708
client = discord.Client(intents=discord.Intents.default())
@client.event
async def on_ready():
    g = client.get_guild(GUILD_ID)
    print('GUILD', g.name if g else None)
    if g:
        print('ROLES', len(g.roles))
        print('CHANNELS', len(g.channels), 'CATEGORIES', len(g.categories))
        print('TOP_ROLES', [(r.name, r.position, r.managed) for r in g.roles[-12:]])
        print('BOT_TOP', g.me.top_role.name, g.me.top_role.position)
        for c in g.categories:
            print('CAT', c.position, repr(c.name), len(c.channels), 'EVERYONE_VIEW', c.overwrites_for(g.default_role).view_channel)
    await client.close()
client.run(os.getenv('DISCORD_TOKEN'))
