import asyncio
import json
from pathlib import Path

import discord
from dotenv import dotenv_values

ROOT = Path(__file__).parent
TOKEN = dotenv_values(ROOT / ".env").get("DISCORD_TOKEN")
GUILD_ID = 1554830636454514708

# Existing category IDs are intentionally used for the one-time repair so duplicate
# categories are repurposed instead of accidentally creating more categories.
CATEGORY_MAP = {
    1563867987130323044: ("╭・𝗦𝗧𝗔𝗥𝗧 𝗛𝗘𝗥𝗘", ["・𝗪𝗲𝗹𝗰𝗼𝗺𝗲", "・𝗖𝗵𝗼𝗼𝘀𝗲・𝗬𝗼𝘂𝗿・𝗥𝗼𝗹𝗲𝘀", "・𝗥𝘂𝗹𝗲𝘀", "・𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁𝘀", "・𝗛𝗼𝘄・𝗜𝘁・𝗪𝗼𝗿𝗸𝘀", "・𝗙𝗔𝗤", "・𝗩𝗲𝗿𝗶𝗳𝗶𝗲𝗱"]),
    1563867989298642944: ("╭・𝗖𝗢𝗠𝗠𝗨𝗡𝗜𝗧𝗬", ["・𝗚𝗲𝗻𝗲𝗿𝗮𝗹", "・𝗚𝗮𝗺𝗶𝗻𝗴・𝗖𝗵𝗮𝘁", "・𝗖𝗹𝗶𝗽𝘀・𝗛𝗶𝗴𝗵𝗹𝗶𝗴𝗵𝘁𝘀", "・𝗠𝗲𝗺𝗲𝘀", "・𝗦𝗰𝗿𝗲𝗲𝗻𝘀𝗵𝗼𝘁𝘀", "・𝗟𝗙𝗚", "・𝗘𝘃𝗲𝗻𝘁𝘀", "・𝗚𝗶𝘃𝗲𝗮𝘄𝗮𝘆𝘀", "・𝗦𝗵𝗼𝘄𝗰𝗮𝘀𝗲", "・𝗥𝗲𝘀𝗼𝘂𝗿𝗰𝗲𝘀", "・𝗖𝗼𝗻𝘁𝗮𝗰𝘁", "・𝗦𝘂𝗴𝗴𝗲𝘀𝘁𝗶𝗼𝗻𝘀", "・𝗖𝗿𝗲𝗮𝘁𝗼𝗿・𝗛𝘂𝗯"]),
    1563867991504855051: ("╭・𝗖𝗟𝗜𝗘𝗡𝗧 𝗛𝗨𝗕", ["・𝗖𝗹𝗶𝗲𝗻𝘁・𝗛𝗲𝗹𝗽", "・𝗣𝗿𝗼𝗷𝗲𝗰𝘁・𝗥𝗲𝗾𝘂𝗲𝘀𝘁𝘀", "・𝗥𝗲𝗾𝘂𝗶𝗿𝗲𝗺𝗲𝗻𝘁𝘀", "・𝗔𝗰𝘁𝗶𝘃𝗲・𝗣𝗿𝗼𝗷𝗲𝗰𝘁𝘀", "・𝗖𝗹𝗶𝗲𝗻𝘁・𝗙𝗲𝗲𝗱𝗯𝗮𝗰𝗸"]),
    1563867993820241960: ("╭・𝗧𝗘𝗔𝗠 𝗛𝗤", ["・𝗧𝗲𝗮𝗺・𝗖𝗵𝗮𝘁", "・𝗣𝗿𝗼𝗷𝗲𝗰𝘁𝘀", "・𝗧𝗮𝘀𝗸𝘀", "・𝗥𝗲𝘀𝗼𝘂𝗿𝗰𝗲𝘀", "・𝗜𝗱𝗲𝗮𝘀", "・𝗪𝗶𝗻𝘀", "・𝗦𝘁𝗮𝗻𝗱𝘂𝗽"]),
    1563867996013985863: ("╭・𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦", ["・𝗔𝗱𝗺𝗶𝗻", "・𝗟𝗲𝗮𝗱𝘀", "・𝗦𝗮𝗹𝗲𝘀", "・𝗙𝗶𝗻𝗮𝗻𝗰𝗲", "・𝗟𝗼𝗴𝘀", "・𝗣𝗹𝗮𝗻𝗻𝗶𝗻𝗴"]),
    1563867999864234026: ("╭・𝗔𝗣𝗣𝗦 & 𝗧𝗢𝗢𝗟𝗦", ["・𝗕𝗼𝘁・𝗖𝗼𝗻𝘁𝗿𝗼𝗹", "・𝗔𝗽𝗽𝘀・𝗜𝗻𝘁𝗲𝗴𝗿𝗮𝘁𝗶𝗼𝗻𝘀", "・𝗔𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗼𝗻"]),
    1563868179724374036: ("╭・𝗖𝗢𝗠𝗠𝗨𝗡𝗜𝗧𝗬 𝗩𝗢𝗜𝗖𝗘", ["・𝗥𝘂𝗽𝘇𝗵𝗮 𝗟𝗼𝘂𝗻𝗴𝗲", "・𝗧𝗲𝗮𝗺 𝗥𝗼𝗼𝗺", "・𝗖𝗹𝗶𝗲𝗻𝘁 𝗖𝗮𝗹𝗹", "・𝗙𝗼𝗰𝘂𝘀 𝗥𝗼𝗼𝗺", "・𝗔𝗙𝗞"]),
    1563875014309052540: ("╭・𝗠𝗘𝗗𝗜𝗔 & 𝗖𝗢𝗡𝗧𝗘𝗡𝗧", ["・𝗖𝗹𝗶𝗽𝘀・𝗛𝗶𝗴𝗵𝗹𝗶𝗴𝗵𝘁𝘀", "・𝗦𝗰𝗿𝗲𝗲𝗻𝘀𝗵𝗼𝘁𝘀", "・𝗦𝗵𝗼𝘄𝗰𝗮𝘀𝗲", "・𝗖𝗿𝗲𝗮𝘁𝗼𝗿・𝗔𝘀𝘀𝗲𝘁𝘀", "・𝗖𝗼𝗻𝘁𝗲𝗻𝘁・𝗜𝗱𝗲𝗮𝘀", "・𝗦𝗼𝗰𝗶𝗮𝗹𝘀", "・𝗘𝘃𝗲𝗻𝘁𝘀", "・𝗚𝗶𝘃𝗲𝗮𝘄𝗮𝘆𝘀", "・𝗥𝗲𝘀𝗼𝘂𝗿𝗰𝗲𝘀", "・𝗣𝗮𝗿𝘁𝗻𝗲𝗿𝘀𝗵𝗶𝗽𝘀", "・𝗖𝗼𝗻𝘁𝗲𝗻𝘁・𝗙𝗲𝗲𝗱𝗯𝗮𝗰𝗸"]),
    1563875023826194513: ("╭・𝗦𝗧𝗔𝗙𝗙 𝗧𝗢𝗢𝗟𝗦", ["・𝗕𝗼𝘁・𝗖𝗼𝗻𝘁𝗿𝗼𝗹", "・𝗜𝗻𝘁𝗲𝗴𝗿𝗮𝘁𝗶𝗼𝗻𝘀", "・𝗔𝘂𝘁𝗼𝗺𝗮𝘁𝗶𝗼𝗻"]),
    1563875026195710052: ("╭・𝗩𝗔𝗟𝗢𝗥𝗔𝗡𝗧", ["・𝗖𝗵𝗮𝘁", "・𝗟𝗙𝗚", "・𝗖𝗹𝗶𝗽𝘀", "・𝗩𝗮𝗹𝗼𝗿𝗮𝗻𝘁 𝗦𝗾𝘂𝗮𝗱"]),
    1563875054373044224: ("╭・𝗠𝗜𝗡𝗘𝗖𝗥𝗔𝗙𝗧", ["・𝗖𝗵𝗮𝘁", "・𝗟𝗙𝗚", "・𝗕𝘂𝗶𝗹𝗱𝘀", "・𝗠𝗶𝗻𝗲𝗰𝗿𝗮𝗳𝘁"]),
    1563875085796774069: ("╭・𝗚𝗧𝗔 𝗩", ["・𝗖𝗵𝗮𝘁", "・𝗟𝗙𝗚", "・𝗖𝗹𝗶𝗽𝘀", "・𝗚𝗧𝗔 𝗦𝗾𝘂𝗮𝗱"]),
    1563875119078834266: ("╭・𝗖𝗦𝟮", ["・𝗖𝗵𝗮𝘁", "・𝗟𝗙𝗚", "・𝗖𝗹𝗶𝗽𝘀", "・𝗖𝗦𝟮 𝗦𝗾𝘂𝗮𝗱"]),
    1563875149357514894: ("╭・𝗙𝗢𝗥𝗧𝗡𝗜𝗧𝗘", ["・𝗖𝗵𝗮𝘁", "・𝗟𝗙𝗚", "・𝗖𝗹𝗶𝗽𝘀", "・𝗙𝗼𝗿𝘁𝗻𝗶𝘁𝗲 𝗦𝗾𝘂𝗮𝗱"]),
    1563875179849977866: ("╭・𝗥𝗢𝗕𝗟𝗢𝗫", ["・𝗖𝗵𝗮𝘁", "・𝗟𝗙𝗚", "・𝗚𝗮𝗺𝗲𝘀", "・𝗥𝗼𝗯𝗹𝗼𝘅"]),
    1563875217892315140: ("╭・𝗔𝗠𝗢𝗡𝗚 𝗨𝗦", ["・𝗖𝗵𝗮𝘁", "・𝗟𝗙𝗚", "・𝗚𝗮𝗺𝗲𝘀", "・𝗔𝗺𝗼𝗻𝗴 𝗨𝘀 𝗟𝗼𝗯𝗯𝘆"]),
    1563875251748601978: ("╭・𝗔𝗣𝗘𝗫 𝗟𝗘𝗚𝗘𝗡𝗗𝗦", ["・𝗖𝗵𝗮𝘁", "・𝗟𝗙𝗚", "・𝗖𝗹𝗶𝗽𝘀", "・𝗔𝗽𝗲𝘅 𝗦𝗾𝘂𝗮𝗱"]),
    1563875285068414996: ("╭・𝗕𝗚𝗠𝗜 • 𝗣𝗨𝗕𝗚", ["・𝗖𝗵𝗮𝘁", "・𝗟𝗙𝗚", "・𝗖𝗹𝗶𝗽𝘀", "・𝗕𝗚𝗠𝗜 / 𝗣𝗨𝗕𝗚 𝗦𝗾𝘂𝗮𝗱"]),
    1563875314319360101: ("╭・𝗢𝗧𝗛𝗘𝗥 𝗚𝗔𝗠𝗘𝗦", ["・𝗖𝗵𝗮𝘁", "・𝗟𝗙𝗚", "・𝗚𝗮𝗺𝗲・𝗥𝗲𝗰𝗼𝗺𝗺𝗲𝗻𝗱𝗮𝘁𝗶𝗼𝗻𝘀", "・𝗢𝘁𝗵𝗲𝗿 𝗚𝗮𝗺𝗲𝘀"]),
    1563875427951575071: ("╭・𝗘𝗩𝗘𝗡𝗧 𝗩𝗢𝗜𝗖𝗘", ["・𝗘𝘃𝗲𝗻𝘁 𝗟𝗼𝘂𝗻𝗴𝗲", "・𝗚𝗮𝗺𝗲 𝗡𝗶𝗴𝗵𝘁", "・𝗧𝗼𝘂𝗿𝗻𝗮𝗺𝗲𝗻𝘁 𝗥𝗼𝗼𝗺", "・𝗖𝗵𝗶𝗹𝗹 𝗥𝗼𝗼𝗺", "・𝗘𝘃𝗲𝗻𝘁 𝗔𝗙𝗞"]),
}

# Public-first ordering, then gaming, then business/staff areas.
CATEGORY_ORDER = [
    1563867987130323044, 1563867989298642944, 1563875014309052540,
    1563875026195710052, 1563875054373044224, 1563875085796774069,
    1563875119078834266, 1563875149357514894, 1563875179849977866,
    1563875217892315140, 1563875251748601978, 1563875285068414996,
    1563875314319360101, 1563868179724374036, 1563875427951575071,
    1563867991504855051, 1563867993820241960, 1563867996013985863,
    1563867999864234026, 1563875023826194513,
]

class RepairClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.last_request = 0.0

    async def safe_edit(self, channel, **kwargs):
        # One channel endpoint has its own rate bucket; a short pause also keeps us
        # comfortably below the global API limit. 429s are handled by Retry-After.
        await asyncio.sleep(0.9)
        while True:
            try:
                await channel.edit(**kwargs, reason="Rupzha professional server cleanup")
                return True
            except discord.HTTPException as exc:
                if exc.status != 429:
                    print(f"ERROR {channel.id} {channel.name}: {exc}")
                    return False
                retry = getattr(exc, "retry_after", None) or 5
                print(f"429 on {channel.id}; waiting {retry:.1f}s")
                await asyncio.sleep(float(retry) + 1)

    async def on_ready(self):
        guild = self.get_guild(GUILD_ID)
        if guild is None:
            print("Guild not found")
            await self.close(); return

        snapshot = []
        for c in guild.channels:
            snapshot.append({"id": c.id, "name": c.name, "type": str(c.type), "category_id": getattr(c.category, "id", None), "position": c.position})
        (ROOT / "docs" / "rupzha-before-cleanup.json").write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))
        print(f"Snapshot saved: {len(snapshot)} channels")

        for category_id, (new_category_name, desired_names) in CATEGORY_MAP.items():
            category = guild.get_channel(category_id)
            if category is None:
                print(f"MISSING CATEGORY {category_id}")
                continue
            if category.name != new_category_name:
                print(f"CATEGORY: {category.name} -> {new_category_name}")
                await self.safe_edit(category, name=new_category_name)

            children = sorted(category.channels, key=lambda c: c.position)
            if len(children) != len(desired_names):
                print(f"COUNT MISMATCH {category.id}: found {len(children)}, expected {len(desired_names)}")
                continue
            for child, desired in zip(children, desired_names):
                if child.name != desired:
                    print(f"CHANNEL: {child.name} -> {desired}")
                    await self.safe_edit(child, name=desired)

        # Re-fetch after renames so position changes use fresh objects.
        await guild.fetch_channels()
        fresh = {c.id: c for c in guild.channels}
        for target_position, category_id in enumerate(CATEGORY_ORDER):
            category = fresh.get(category_id)
            if category and category.position != target_position:
                print(f"ORDER: {category.name} -> {target_position}")
                await self.safe_edit(category, position=target_position)

        await asyncio.sleep(2)
        await guild.fetch_channels()
        final = []
        for c in guild.channels:
            final.append({"id": c.id, "name": c.name, "type": str(c.type), "category_id": getattr(c.category, "id", None), "position": c.position})
        (ROOT / "docs" / "rupzha-after-cleanup.json").write_text(json.dumps(final, indent=2, ensure_ascii=False))
        print(f"FINAL CHANNELS: {len(final)}")
        print("BLANK:", [x for x in final if x["name"] in ("", "・")])
        await self.close()

if not TOKEN:
    raise SystemExit("DISCORD_TOKEN missing")
RepairClient().run(TOKEN)
