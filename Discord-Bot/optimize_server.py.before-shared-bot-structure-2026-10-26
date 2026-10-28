import asyncio
from pathlib import Path

import discord
from dotenv import dotenv_values

ROOT = Path(__file__).parent
TOKEN = dotenv_values(ROOT / ".env").get("DISCORD_TOKEN")
GUILD_ID = 1554830636454514708

VOICE_CATEGORY = "╭・𝗩𝗢𝗜𝗖𝗘"
VOICE_CHANNELS = [
    "🛋️・・𝗥𝘂𝗽𝘇𝗵𝗮・𝗟𝗼𝘂𝗻𝗴𝗲",
    "🎮・・𝗚𝗮𝗺𝗲・𝗡𝗶𝗴𝗵𝘁",
    "🌙・・𝗖𝗵𝗶𝗹𝗹",
    "💤・・𝗔𝗙𝗞",
]

GAME_CATEGORY_NAMES = {
    "╭・𝗚𝗔𝗠𝗘・VALORANT": "╭・𝗚𝗔𝗠𝗘・𝗩𝗔𝗟𝗢𝗥𝗔𝗡𝗧",
    "╭・𝗚𝗔𝗠𝗘・MINECRAFT": "╭・𝗚𝗔𝗠𝗘・𝗠𝗜𝗡𝗘𝗖𝗥𝗔𝗙𝗧",
    "╭・𝗚𝗔𝗠𝗘・GTA V": "╭・𝗚𝗔𝗠𝗘・𝗚𝗧𝗔・𝗩",
    "╭・𝗚𝗔𝗠𝗘・CS2": "╭・𝗚𝗔𝗠𝗘・𝗖𝗦𝟮",
    "╭・𝗚𝗔𝗠𝗘・FORTNITE": "╭・𝗚𝗔𝗠𝗘・𝗙𝗢𝗥𝗧𝗡𝗜𝗧𝗘",
    "╭・𝗚𝗔𝗠𝗘・ROBLOX": "╭・𝗚𝗔𝗠𝗘・𝗥𝗢𝗕𝗟𝗢𝗫",
    "╭・𝗚𝗔𝗠𝗘・AMONG US": "╭・𝗚𝗔𝗠𝗘・𝗔𝗠𝗢𝗡𝗚・𝗨𝗦",
    "╭・𝗚𝗔𝗠𝗘・APEX LEGENDS": "╭・𝗚𝗔𝗠𝗘・𝗔𝗣𝗘𝗫・𝗟𝗘𝗚𝗘𝗡𝗗𝗦",
    "╭・𝗚𝗔𝗠𝗘・BGMI / PUBG": "╭・𝗚𝗔𝗠𝗘・𝗕𝗚𝗠𝗜・／・𝗣𝗨𝗕𝗚",
    "╭・𝗚𝗔𝗠𝗘・OTHER GAMES": "╭・𝗚𝗔𝗠𝗘・𝗢𝗧𝗛𝗘𝗥・𝗚𝗔𝗠𝗘𝗦",
    "・𝗚𝗔𝗠𝗘・OTHER GAMES": "╭・𝗚𝗔𝗠𝗘・𝗢𝗧𝗛𝗘𝗥・𝗚𝗔𝗠𝗘𝗦",
}

BOT_CANONICAL_NAMES = {
    "Dank Memer": "🤖・・𝗗𝗮𝗻𝗸・𝗠𝗲𝗺𝗲𝗿",
    "Diva": "🤖・・𝗗𝗶𝘃𝗮",
    "Freebee": "🤖・・𝗙𝗿𝗲𝗲𝗯𝗲𝗲",
    "Hazy": "🤖・・𝗛𝗮𝘇𝘆",
    "Mimu": "🤖・・𝗠𝗶𝗺𝘂",
    "OwO": "🤖・・𝗢𝘄𝗢",
    "Poké-Name": "🤖・・𝗣𝗼𝗸𝗲・𝗡𝗮𝗺𝗲",
    "Pokétwo": "🎮・・𝗣𝗼𝗸𝗲𝘁𝘄𝗼",
    "Sapphire": "🤖・・𝗦𝗮𝗽𝗽𝗵𝗶𝗿𝗲",
    "Tune 🌷": "🤖・・𝗧𝘂𝗻𝗲",
    "Word Chain Bot Indently": "🤖・・𝗪𝗼𝗿𝗱・𝗖𝗵𝗮𝗶𝗻",
    "Koya": "🌸・・𝗞𝗼𝘆𝗮",
}

BOT_ALIASES = {
    "Dank Memer": {"🤖・・𝗗𝗮𝗻𝗸・𝗠𝗲𝗺𝗲𝗿", "🤖・・dank-memer"},
    "Diva": {"🤖・・𝗗𝗶𝘃𝗮", "🤖・・𝗶𝘃𝗮", "🤖・・diva"},
    "Freebee": {"🤖・・𝗙𝗿𝗲𝗲𝗯𝗲𝗲", "🤖・・𝗿𝗲𝗲𝗯𝗲𝗲", "🤖・・freebee", "🤖・・reebee"},
    "Hazy": {"🤖・・𝗛𝗮𝘇𝘆", "🤖・・𝗮𝘇𝘆", "🤖・・hazy", "🤖・・azy"},
    "Mimu": {"🤖・・𝗠𝗶𝗺𝘂", "🤖・・mimu"},
    "OwO": {"🤖・・𝗢𝘄𝗢", "🤖・・𝘄𝗢", "🤖・・𝘄𝗼", "🤖・・owo"},
    "Poké-Name": {"🤖・・𝗣𝗼𝗸𝗲・𝗡𝗮𝗺𝗲", "🤖・・𝗼𝗸𝗲・𝗡𝗮𝗺𝗲", "🤖・・𝗼𝗸𝗲・𝗻𝗮𝗺𝗲", "🤖・・oké-name", "🤖・・poké-name"},
    "Pokétwo": {"🎮・・𝗣𝗼𝗸𝗲𝘁𝘄𝗼", "🤖・・𝗼𝗸𝗲𝘁𝘄𝗼", "🤖・・okétwo", "🤖・・pokétwo"},
    "Sapphire": {"🤖・・𝗦𝗮𝗽𝗽𝗵𝗶𝗿𝗲", "🤖・・𝗮𝗽𝗽𝗵𝗶𝗿𝗲", "🤖・・sapphire", "🤖・・apphire"},
    "Tune 🌷": {"🤖・・𝗧𝘂𝗻𝗲", "🤖・・𝘂𝗻𝗲", "🤖・・tune", "🤖・・une"},
    "Word Chain Bot Indently": {"🤖・・𝗪𝗼𝗿𝗱・𝗖𝗵𝗮𝗶𝗻", "🤖・・𝗼𝗿𝗱・𝗰𝗵𝗮𝗶𝗻", "🤖・・𝗼𝗿𝗱・𝗖𝗵𝗮𝗶𝗻", "🤖・・word-chain-bot-indently", "🤖・・ord-chain-bot-indently", "🤖・・word-chain-bot-indently"},
    "Koya": {"🌸・・𝗞𝗼𝘆𝗮", "🤖・・koya"},
}

class Optimizer(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())

    async def recent_message_count(self, channel):
        count = 0
        try:
            async for _ in channel.history(limit=1):
                count += 1
        except discord.HTTPException:
            return 1
        return count

    async def on_ready(self):
        guild = self.get_guild(GUILD_ID)
        if not guild:
            print("GUILD NOT FOUND")
            await self.close()
            return

        print(f"OPTIMIZE START · {guild.name} · {len(guild.channels)} channels · {len(guild.roles)} roles")

        # 1. Fix the dedicated voice category: these four channels must be actual VoiceChannels.
        voice_category = discord.utils.get(guild.categories, name=VOICE_CATEGORY)
        if voice_category:
            existing = {c.name: c for c in voice_category.channels}
            for name in VOICE_CHANNELS:
                old = existing.get(name)
                if old and isinstance(old, discord.VoiceChannel):
                    continue
                if old and isinstance(old, discord.TextChannel):
                    has_messages = await self.recent_message_count(old)
                    new = await guild.create_voice_channel(
                        name,
                        category=voice_category,
                        overwrites=old.overwrites,
                        position=old.position,
                        user_limit=0,
                        reason="RupZha optimization: convert voice text channel to voice channel",
                    )
                    print(f"VOICE FIX · {name} · text->{new.id} voice")
                    if has_messages == 0:
                        await old.delete(reason="RupZha optimization: remove obsolete text version of voice channel")
                        print(f"VOICE CLEAN · deleted empty text channel {old.id}")
                    else:
                        archive_name = f"💬・・𝗔𝗿𝗰𝗵𝗶𝘃𝗲・{name.split('・・', 1)[-1]}"
                        await old.edit(name=archive_name[:100], reason="RupZha optimization: preserve existing text history")
                        print(f"VOICE PRESERVE · {old.id} kept as {archive_name}")
                elif old is None:
                    new = await guild.create_voice_channel(name, category=voice_category, reason="RupZha optimization: restore missing voice channel")
                    print(f"VOICE CREATE · {name} · {new.id}")

            # Fix the category's order so the four rooms are predictable.
            fresh = [c for c in voice_category.channels if isinstance(c, discord.VoiceChannel)]
            by_name = {c.name: c for c in fresh}
            for index, name in enumerate(VOICE_CHANNELS):
                ch = by_name.get(name)
                if ch and ch.position != index:
                    await ch.edit(position=index, reason="RupZha optimization: voice channel ordering")
        else:
            print("WARN · voice category missing")

        # 2. Normalize every game category so the sidebar has one consistent visual language.
        for old_name, new_name in GAME_CATEGORY_NAMES.items():
            category = discord.utils.get(guild.categories, name=old_name)
            if category and category.name != new_name:
                await asyncio.sleep(1.5)
                await category.edit(name=new_name, reason="RupZha optimization: consistent game category typography")
                print(f"CATEGORY NAME · {old_name} -> {new_name}")

        # 3. Normalize the bot-command area to one clean channel per utility bot.
        bot_category = discord.utils.get(guild.categories, name="╭・𝗕𝗢𝗧・𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦")
        if bot_category:
            for bot_name, desired in BOT_CANONICAL_NAMES.items():
                candidates = [c for c in bot_category.text_channels if c.name in BOT_ALIASES[bot_name]]
                if not candidates and bot_name in {"Mimu", "Dank Memer"}:
                    await asyncio.sleep(1.5)
                    channel = await guild.create_text_channel(desired, category=bot_category, reason=f"RupZha optimization: dedicated {bot_name} command channel")
                    candidates = [channel]
                    print(f"BOT CREATE · {bot_name} · {channel.id}")
                if not candidates:
                    continue
                counts = []
                for channel in candidates:
                    counts.append((await self.recent_message_count(channel), channel))
                counts.sort(key=lambda item: (item[0] > 0, item[0], -item[1].id), reverse=True)
                keep = counts[0][1]
                if keep.name != desired:
                    await asyncio.sleep(1.5)
                    old_name = keep.name
                    await keep.edit(name=desired, reason="RupZha optimization: consistent bot channel typography")
                    print(f"BOT NAME · {old_name} -> {desired}")
                for message_count, duplicate in counts[1:]:
                    if message_count == 0:
                        await asyncio.sleep(1.5)
                        await duplicate.delete(reason=f"RupZha optimization: remove duplicate {bot_name} command channel")
                        print(f"BOT DELETE · {duplicate.id} · {duplicate.name}")
                    else:
                        print(f"BOT KEEP HISTORY · {duplicate.id} · {duplicate.name}")

            # Delete any leftover generic bot channels that no longer correspond to a live bot.
            live_names = set(BOT_CANONICAL_NAMES.values()) | {"🌸・・𝗞𝗼𝘆𝗮"}
            for channel in list(bot_category.text_channels):
                if channel.name in live_names:
                    continue
                if channel.name.startswith("🤖・・") and await self.recent_message_count(channel) == 0:
                    await asyncio.sleep(1.5)
                    await channel.delete(reason="RupZha optimization: remove orphaned bot command channel")
                    print(f"BOT ORPHAN DELETE · {channel.id} · {channel.name}")

        # 4. Remove the temporary Chill archive if it is empty; history is preserved otherwise.
        archive = discord.utils.get(guild.text_channels, name="💬・・𝗔𝗿𝗰𝗵𝗶𝘃𝗲・𝗖𝗵𝗶𝗹𝗹")
        if archive and await self.recent_message_count(archive) == 0:
            await asyncio.sleep(1.5)
            await archive.delete(reason="RupZha optimization: remove empty temporary voice archive")
            print(f"ARCHIVE DELETE · {archive.id}")

        await guild.fetch_channels()
        voice_category = discord.utils.get(guild.categories, name=VOICE_CATEGORY)
        if voice_category:
            print("VOICE FINAL", [(c.name, type(c).__name__) for c in voice_category.channels])
        bot_category = discord.utils.get(guild.categories, name="╭・𝗕𝗢𝗧・𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦")
        if bot_category:
            print("BOT FINAL", [c.name for c in bot_category.text_channels])
        print(f"OPTIMIZE COMPLETE · {len(guild.channels)} channels · {len(guild.categories)} categories")
        await self.close()

if not TOKEN:
    raise SystemExit("DISCORD_TOKEN missing")

Optimizer().run(TOKEN)
