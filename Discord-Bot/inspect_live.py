import json, urllib.request
from pathlib import Path
from dotenv import dotenv_values
cfg=dotenv_values(Path(__file__).parent/'.env')
req=urllib.request.Request('https://discord.com/api/v10/guilds/1554830636454514708/channels',headers={'Authorization':'Bot '+cfg['DISCORD_TOKEN']})
cs=json.load(urllib.request.urlopen(req))
for c in sorted(cs,key=lambda x:x['position']):
    if c['type']==4:
        print('\nCAT',c['id'],c['position'],c['name'])
        children=sorted([z for z in cs if z.get('parent_id')==c['id']],key=lambda z:z['position'])
        for x in children: print(' ',x['id'],x['type'],x['position'],x['name'])
