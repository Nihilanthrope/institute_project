import json
import time
import unicodedata
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

GUILD_ID = '1554830636454514708'
BASE = 'https://discord.com/api/v10'

def load_token():
    for line in Path('.env').read_text().splitlines():
        if line.replace(' ', '').startswith('DISCORD_TOKEN='):
            return line.split('=', 1)[1].strip().strip('"').strip("'")
    raise RuntimeError('DISCORD_TOKEN not found')

token = load_token()
headers = {'Authorization': f'Bot {token}', 'User-Agent': 'RupZha-Channel-Cleanup/1.0'}

rules = [
    ('welcome', '👋'), ('rules', '📜'), ('announcement', '📢'), ('update', '📣'),
    ('choose', '🎯'), ('role', '🎭'), ('general', '💬'), ('chat', '💬'),
    ('valorant', '🎯'), ('minecraft', '⛏️'), ('gta', '🚗'), ('cs2', '🔫'),
    ('fortnite', '🏹'), ('roblox', '🧱'), ('among us', '🚀'), ('apex', '🏹'),
    ('bgmi', '🔫'), ('pubg', '🔫'), ('lfg', '🔎'), ('clip', '🎬'), ('build', '🧱'), ('game', '🎮'),
    ('sales', '💰'), ('finance', '💳'), ('lead', '📈'), ('log', '📋'),
    ('planning', '🗓️'), ('backup', '💾'), ('ticket', '🎫'), ('dashboard', '📊'),
    ('activity', '📈'), ('level', '🏆'), ('integration', '🔗'), ('automation', '⚙️'),
    ('security', '🔐'), ('anti-raid', '🛡️'), ('afk', '💤'), ('voice', '🔊'),
    ('music', '🎵'), ('media', '🖼️'), ('bot', '🤖'), ('staff', '🛠️'),
    ('how', '❓'), ('faq', '❔'), ('meme', '😂'), ('screenshot', '📸'), ('showcase', '🌟'),
    ('contact', '📞'), ('event', '🎉'), ('giveaway', '🎁'), ('tournament', '🏆'),
    ('lounge', '🛋️'), ('chill', '🌙'), ('client', '🤝'), ('project request', '📩'),
    ('project status', '📊'), ('feedback', '💭'), ('projects', '📁'), ('tasks', '✅'),
    ('ideas', '💡'), ('wins', '🏅'),
]
emoji_chars = tuple(e for _, e in rules)

def api(method, path, body=None):
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode()
    req = Request(BASE + path, data=data, headers={**headers, 'Content-Type': 'application/json'}, method=method)
    with urlopen(req, timeout=15) as r:
        return json.loads(r.read()) if r.readable() else None

channels = api('GET', f'/guilds/{GUILD_ID}/channels')
changed = 0
for ch in channels:
    if ch['type'] == 4:  # category
        if ch['name'].startswith('🎮・'):
            new_name = ch['name'][3:]
            api('PATCH', f"/channels/{ch['id']}", {'name': new_name})
            print(f'CATEGORY {ch["name"]} -> {new_name}')
            time.sleep(0.8)
        continue
    name = ch['name']
    repairs = {
        '❓・・𝗦𝗵𝗼𝘄𝗰𝗮𝘀𝗲': '🌟・・𝗦𝗵𝗼𝘄𝗰𝗮𝘀𝗲',
        '🤝・・𝗖𝗹𝗶𝗲𝗻𝘁・𝗙𝗲𝗲𝗱𝗯𝗮𝗰𝗸': '💭・・𝗖𝗹𝗶𝗲𝗻𝘁・𝗙𝗲𝗲𝗱𝗯𝗮𝗰𝗸',
    }
    if name in repairs:
        new_name = repairs[name]
        api('PATCH', f"/channels/{ch['id']}", {'name': new_name})
        print(f'REPAIR {name} -> {new_name}')
        changed += 1
        time.sleep(0.8)
        continue
    if name.startswith(emoji_chars):
        continue
    normalized = unicodedata.normalize('NFKC', name).lower().replace('・', ' ')
    emoji = next((e for key, e in rules if key in normalized), None)
    if not emoji:
        continue
    new_name = f'{emoji}・{name}'
    try:
        api('PATCH', f"/channels/{ch['id']}", {'name': new_name})
        print(f'CHANNEL {name} -> {new_name}')
        changed += 1
        time.sleep(0.8)
    except HTTPError as exc:
        print(f'SKIP {name}: HTTP {exc.code}')

print('UNHANDLED CHANNELS:')
for ch in channels:
    if ch['type'] != 4 and not ch['name'].startswith(emoji_chars):
        print(f"UNHANDLED | {ch['name']}")
print(f'DONE: {changed} channel names updated')
