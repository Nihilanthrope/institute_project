import os
import sys
import fcntl
import asyncio
import sqlite3
import unicodedata
from datetime import timedelta
from pathlib import Path
import discord
from dotenv import load_dotenv

from storage import Database
from moderation import JoinGuard, can_execute_moderation, get_recent_cases, is_staff, log_security_event, record_case, security_log_channel_name
from tickets import TicketService, TICKET_CATEGORIES, ticket_type_definition, build_ticket_category_overwrites, build_ticket_overwrites
from community import CommunityService, level_for_xp
from operations import build_client_status_embed, can_edit_project, can_view_project, create_internal_case, get_project_status, set_project_status
from verify_full_upgrade import readiness_lines, verify_live_guild

load_dotenv()

# Only one RupZha gateway process may run on this machine. The lock is acquired
# only by the real executable entry point so tests/imports remain side-effect free.
INSTANCE_LOCK_PATH = Path("/tmp/rupzha-bot.lock")
_INSTANCE_LOCK = None

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1554830636454514708
TICKET_ROOMS_CATEGORY = "╭・𝗧𝗜𝗖𝗞𝗘𝗧・𝗥𝗢𝗢𝗠𝗦"
TICKET_ARCHIVE_CATEGORY = "╭・𝗧𝗜𝗖𝗞𝗘𝗧・𝗔𝗥𝗖𝗛𝗜𝗩𝗘"
TICKET_TRANSCRIPT_DIR = Path(__file__).with_name("transcripts")
BOT_COMMAND_CHANNEL_NAME = "🤖・・𝗕𝗼𝘁・𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀"
DEDICATED_BOT_CHANNELS = {
    "OwO": "🤖・・𝗢𝘄𝗢",
    "Pokétwo": "🎮・・𝗣𝗼𝗸𝗲𝘁𝘄𝗼",
    "Koya": "🌸・・𝗞𝗼𝘆𝗮",
}
LEGACY_OWO_COMMANDS = {
    "cash", "cowoncy", "hunt", "battle", "daily", "claim", "give", "pay", "sell",
    "buy", "shop", "slots", "coinflip", "blackjack", "drop", "crate", "pets",
    "zoo", "inv", "inventory", "autohunt", "owodex", "top", "profile", "rank",
    "pray", "curse", "cookie", "ship", "help", "ping", "stats", "prefix",
}

def legacy_bot_prefix_is_blocked(content: str, channel_name: str) -> bool:
    """Block legacy prefix commands outside the single public bot-command channel."""
    if channel_name in set(BOT_COMMAND_CHANNELS_BY_BOT.values()) | set(DEDICATED_BOT_CHANNELS.values()):
        return False
    text = content.strip()
    if text.casefold().startswith("p!") and len(text) > 2 and not text[2].isspace():
        return True
    parts = text.casefold().split(maxsplit=1)
    return len(parts) == 2 and parts[0] == "owo" and parts[1].split(maxsplit=1)[0] in LEGACY_OWO_COMMANDS
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing from .env")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = discord.Client(
    intents=intents,
    guild_ready_timeout=10.0,
    chunk_guilds_at_startup=False,
)

DB_PATH = Path(os.getenv("RUPZHA_DB_PATH", Path(__file__).with_name("rupzha.db")))
WELCOME_GIF_PATH = Path(__file__).with_name("assets") / "rupzha-welcome.gif"
db = Database(DB_PATH)
db.initialize()
join_guard = JoinGuard(window_seconds=10.0, threshold=8)
ticket_service = TicketService(db)
community_service = CommunityService(db)
reminder_task = None
ticket_lifecycle_task = None

ROLE_ORDER = [
    "Founder", "Co-Founder", "Administrator", "Operations", "Manager",
    "Moderator", "Support", "Developer", "Designer", "Content Creator",
    "Client", "Verified", "Member", "Valorant", "Minecraft", "GTA V",
    "CS2", "Fortnite", "Roblox", "Among Us", "Apex Legends",
    "BGMI / PUBG", "Other Games",
]

GAME_ROLES = ROLE_ORDER[13:]
STAFF_ROLES = ROLE_ORDER[:7]

# Strict role policy: permissions represent power; category overwrites represent access.
OPTIONAL_ROLE_POLICY = {
    "Trial Moderator": {"permissions": 0, "auto_assign": False},
    "Event Host": {"permissions": 0, "auto_assign": False},
    "QA / Tester": {"permissions": 0, "auto_assign": False},
    "Partner": {"permissions": 0, "auto_assign": False},
    "Community Helper": {"permissions": 0, "auto_assign": False},
}

ROLE_PERMISSION_POLICY = {
    "Founder": discord.Permissions(administrator=True),
    "Co-Founder": discord.Permissions(administrator=True),
    "Administrator": discord.Permissions(administrator=True),
    "Operations": discord.Permissions(manage_guild=True, manage_channels=True, manage_messages=True, view_audit_log=True, kick_members=True, ban_members=True),
    "Manager": discord.Permissions(manage_messages=True, manage_threads=True, view_audit_log=True),
    "Moderator": discord.Permissions(manage_messages=True, manage_threads=True, moderate_members=True, kick_members=True),
    "Rupzha Bot": discord.Permissions(view_channel=True, send_messages=True, embed_links=True, attach_files=True, read_message_history=True, use_application_commands=True, manage_channels=True, manage_roles=True, manage_messages=True, manage_threads=True, kick_members=True, ban_members=True, moderate_members=True),
    "Support": discord.Permissions(manage_threads=True),
    "Developer": discord.Permissions.none(),
    "Designer": discord.Permissions.none(),
    "Content Creator": discord.Permissions.none(),
    "Client": discord.Permissions.none(),
    "Verified": discord.Permissions.none(),
    "Member": discord.Permissions.none(),
}
for _game_role in GAME_ROLES:
    ROLE_PERMISSION_POLICY[_game_role] = discord.Permissions.none()
for _optional_role in OPTIONAL_ROLE_POLICY:
    ROLE_PERMISSION_POLICY[_optional_role] = discord.Permissions.none()

CATEGORY_ACCESS_POLICY = {
    "╭・𝗖𝗟𝗜𝗘𝗡𝗧 𝗛𝗨𝗕": {"Client", "Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Support"},
    "╭・𝗧𝗘𝗔𝗠 𝗛𝗤": {"Developer", "Designer", "Content Creator", "Founder", "Co-Founder", "Administrator", "Operations", "Manager"},
    "╭・𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦": {"Founder", "Co-Founder", "Administrator", "Operations"},
    "╭・𝗔𝗣𝗣𝗦 & 𝗧𝗢𝗢𝗟𝗦": {"Founder", "Co-Founder", "Administrator", "Operations"},
    "╭・𝗕𝗢𝗧・𝗟𝗢𝗚𝗦": {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator", "Support"},
    TICKET_ROOMS_CATEGORY: {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator", "Support"},
}

# Utility bots can read public/community channels, but private workspace and
# integration areas stay hidden unless their own policy explicitly permits them.
PRIVATE_WORKSPACE_CATEGORIES = set(CATEGORY_ACCESS_POLICY)

# Child-channel locks tighten category permissions without changing the category model.
# Modes: public_read_only, public_read_only_bot_write, client_read_only,
# restricted_read_only, restricted_bot_write.
CHANNEL_LOCK_POLICY = {
    "・𝗪𝗲𝗹𝗰𝗼𝗺𝗲": {"mode": "public_read_only"},
    "・𝗥𝘂𝗹𝗲𝘀": {"mode": "public_read_only"},
    "・𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁𝘀": {"mode": "public_read_only"},
    "・𝗛𝗼𝘄・𝗜𝘁・𝗪𝗼𝗿𝗸𝘀": {"mode": "public_read_only"},
    "・𝗙𝗔𝗤": {"mode": "public_read_only"},
    "・𝗣𝗿𝗼𝗷𝗲𝗰𝘁・𝗦𝘁𝗮𝘁𝘂𝘀": {"mode": "client_read_only"},
    "・𝗟𝗼𝗴𝘀": {"mode": "restricted_read_only"},
    "・𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆・𝗟𝗼𝗴𝘀": {"mode": "restricted_bot_write", "bot_roles": ["Wick"]},
    "・𝗔𝗻𝘁𝗶𝗥𝗮𝗶𝗱・𝗟𝗼𝗴𝘀": {"mode": "restricted_bot_write", "bot_roles": ["Wick"]},
    "・𝗧𝗶𝗰𝗸𝗲𝘁・𝗣𝗮𝗻𝗲𝗹": {"mode": "public_read_only_bot_write", "bot_roles": ["Ticket Tool", "RupZha"]},
    "・𝗦𝘁𝗮𝘁𝘀・𝗗𝗮𝘀𝗵𝗯𝗼𝗮𝗿𝗱": {"mode": "restricted_bot_write", "bot_roles": ["Statbot"]},
    "・𝗔𝗰𝘁𝗶𝘃𝗶𝘁𝘆・𝗦𝘁𝗮𝘁𝘀": {"mode": "restricted_bot_write", "bot_roles": ["Statbot"]},
    "・𝗟𝗲𝘃𝗲𝗹・𝗨𝗽𝘀": {"mode": "public_read_only_bot_write", "bot_roles": ["Arcane"]},
    "・𝗕𝗮𝗰𝗸𝘂𝗽𝘀": {"mode": "restricted_bot_write", "bot_roles": ["Xenon"]},
    "・𝗖𝗮𝗿𝗹・𝗟𝗼𝗴𝘀": {"mode": "restricted_bot_write", "bot_roles": ["carl-bot"]},
}

READ_ONLY_STAFF_ROLES = {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator", "Support"}

# Third-party utility bots are command-scoped: each bot may send messages and
# receive application commands only in its dedicated channel.
THIRD_PARTY_BOT_CHANNELS = dict(DEDICATED_BOT_CHANNELS)


def third_party_bot_message_allowed(bot_id: int, channel_id: int) -> bool:
    """Final message-boundary guard for dedicated third-party bots."""
    allowed_channel_ids = {
        408785106942164992: 1564050781307670629,  # OwO
        716390085896962058: 1564050784432427168,  # Pokétwo
        276060004262477825: 1564050787070509207,  # Koya
    }
    return allowed_channel_ids.get(int(bot_id), int(channel_id)) == int(channel_id)


def build_application_command_scope(guild_id: int, channel_id: int) -> list[dict[str, object]]:
    """Build the Discord command-permission scope for one dedicated channel.

    This is intentionally a pure data builder: Discord may reject permission
    mutation for commands owned by another application, but the desired scope
    remains explicit and testable rather than being hidden in ad-hoc API calls.
    """
    return [
        {"id": str(int(guild_id)), "type": 1, "permission": False},
        {"id": str(int(channel_id)), "type": 3, "permission": True},
    ]


THIRD_PARTY_BOT_CHANNEL_POLICIES = {
    name: {"bot_role": name, "channel_name": channel}
    for name, channel in DEDICATED_BOT_CHANNELS.items()
}

# One canonical public command channel per utility bot. Aliases are reconciled
# into these names so the setup loop never creates typography duplicates.
# Keep the public bot area intentionally small. Only these three member-facing
# utility bots get dedicated channels; other installed bots stay isolated and
# do not get a channel of their own.
BOT_COMMAND_CHANNELS_BY_BOT = {
    "Dank Memer": BOT_COMMAND_CHANNEL_NAME,
    "Diva": BOT_COMMAND_CHANNEL_NAME,
    "Freebee": BOT_COMMAND_CHANNEL_NAME,
    "Hazy": BOT_COMMAND_CHANNEL_NAME,
    "Mimu": BOT_COMMAND_CHANNEL_NAME,
    "Poké-Name": BOT_COMMAND_CHANNEL_NAME,
    "Sapphire": BOT_COMMAND_CHANNEL_NAME,
    "Tune 🌷": BOT_COMMAND_CHANNEL_NAME,
    "Word Chain Bot Indently": BOT_COMMAND_CHANNEL_NAME,
}

BOT_CHANNEL_ALIASES = {
    "OwO": {"🤖・・𝘄𝗢", "🤖・・𝗢𝘄𝗢"},
    "Pokétwo": {"🎮・・𝗣𝗼𝗸𝗲𝘁𝘄𝗼", "🤖・・𝗽𝗼𝗸étwo", "🤖・・okétwo", "🤖・・pokétwo"},
    "Koya": {"🌸・・𝗞𝗼𝘆𝗮"},
    "Tune 🌷": {"🤖・・𝘂𝗻𝗲", "🤖・・tune"},
    "Hazy": {"🤖・・𝗮𝘇𝘆", "🤖・・hazy"},
    "Word Chain Bot Indently": {"🤖・・𝗼𝗿𝗱・𝗖𝗵𝗮𝗶𝗻", "🤖・・word-chain-bot-indently"},
    "Diva": {"🤖・・𝗶𝘃𝗮", "🤖・・diva"},
    "Poké-Name": {"🤖・・𝗼𝗸𝗲・𝗡𝗮𝗺𝗲", "🤖・・poké-name"},
    "Freebee": {"🤖・・𝗿𝗲𝗲𝗯𝗲𝗲", "🤖・・freebee"},
    "Sapphire": {"🤖・・𝗮𝗽𝗽𝗵𝗮𝗶𝗿𝗲", "🤖・・sapphire", "🤖・・𝗦𝗮𝗽𝗽𝗵𝗶𝗿𝗲"},
    "Mimu": {"🤖・・𝗠𝗶𝗺𝘂"},
    "Dank Memer": {"🤖・・𝗗𝗮𝗻𝗸・𝗠𝗲𝗺𝗲𝗿"},
}

DEDICATED_BOT_CHANNEL_NAMES = {name: channel for name, channel in BOT_COMMAND_CHANNELS_BY_BOT.items()}

def dedicated_bot_channel_name(member_name: str, member_id: int) -> str:
    if member_name in DEDICATED_BOT_CHANNEL_NAMES:
        return DEDICATED_BOT_CHANNEL_NAMES[member_name]
    safe_name = "".join(ch for ch in member_name.lower() if ch.isalnum() or ch in "-_ ").strip().replace(" ", "-")
    return f"🤖・・{safe_name[:80] or str(member_id)}"


SPECIAL_BOT_CHANNEL_POLICIES = {
    "Wick": {"📋・・𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆・𝗟𝗼𝗴𝘀", "📋・・𝗔𝗻𝘁𝗶𝗥𝗮𝗶𝗱・𝗟𝗼𝗴𝘀"},
    "Ticket Tool": {"🎫・・𝗧𝗶𝗰𝗸𝗲𝘁・𝗣𝗮𝗻𝗲𝗹"},
    "Statbot": {"📊・・𝗦𝘁𝗮𝘁𝘀・𝗗𝗮𝘀𝗵𝗯𝗼𝗮𝗿𝗱", "📈・・𝗔𝗰𝘁𝗶𝘃𝗶𝘁𝘆・𝗦𝘁𝗮𝘁𝘀"},
    "Arcane": {"🏆・・𝗟𝗲𝘃𝗲𝗹・𝗨𝗽𝘀"},
    "Xenon": {"💾・・𝗕𝗮𝗰𝗸𝘂𝗽𝘀"},
    "carl-bot": {"📋・・𝗖𝗮𝗿𝗹・𝗟𝗼𝗴𝘀"},
}


def check_bot_command_layout(command_children) -> list[str]:
    names = [channel.name for channel in command_children]
    failures = []
    if names.count(BOT_COMMAND_CHANNEL_NAME) != 1:
        failures.append(f"bot-command-channel:shared=found-{names.count(BOT_COMMAND_CHANNEL_NAME)}")
    for bot_name, channel_name in DEDICATED_BOT_CHANNELS.items():
        count = names.count(channel_name)
        if count != 1:
            failures.append(f"bot-command-channel:{bot_name}=found-{count}")
    allowed = {BOT_COMMAND_CHANNEL_NAME, *DEDICATED_BOT_CHANNELS.values()}
    unexpected = [name for name in names if name not in allowed]
    if unexpected:
        failures.append("bot-command-channel:unexpected=" + ",".join(unexpected))
    return failures


def bot_allowed_channels_for_member(member_name: str, member_id: int) -> set[str]:
    """Resolve a bot's allowlist without case-sensitive name bugs or orphan channels."""
    normalized_name = member_name.casefold()
    for configured_name, channel_name in DEDICATED_BOT_CHANNELS.items():
        if configured_name.casefold() == normalized_name:
            return {channel_name}
    for configured_name, channel_names in SPECIAL_BOT_CHANNEL_POLICIES.items():
        if configured_name.casefold() == normalized_name:
            return set(channel_names)
    for configured_name, channel_name in BOT_COMMAND_CHANNELS_BY_BOT.items():
        if configured_name.casefold() == normalized_name:
            return {channel_name}
    for configured_name, channel_name in DEDICATED_BOT_CHANNEL_NAMES.items():
        if configured_name.casefold() == normalized_name:
            return {channel_name}
    return {dedicated_bot_channel_name(member_name, member_id)}

def build_universal_bot_overwrite(bot_name: str, own_channel_name: str, channel_name: str, is_private: bool = False):
    allowed = channel_name == own_channel_name
    visible = not is_private or allowed
    return {
        "allowed": allowed, "view_channel": visible, "read_message_history": visible,
        "send_messages": allowed, "send_messages_in_threads": allowed,
        "create_public_threads": allowed, "create_private_threads": False,
        "use_application_commands": allowed, "add_reactions": allowed,
    }

def build_third_party_bot_overwrite(bot_name: str, own_channel_name: str, channel_name: str, is_private: bool = False):
    allowed = channel_name == own_channel_name
    visible = not is_private or allowed
    return {
        "allowed": allowed,
        "view_channel": visible,
        "read_message_history": visible,
        "send_messages": allowed,
        "send_messages_in_threads": allowed,
        "create_public_threads": allowed,
        "create_private_threads": False,
        "use_application_commands": allowed,
        "add_reactions": allowed,
    }


def build_game_hub_policy(game: str, role_names: list[str] | set[str]):
    roles = set(role_names)
    return {
        "everyone_view": False,
        "allowed_game_role": game,
        "blocked_game_roles": (set(GAME_ROLES) - {game}) & roles,
        "blocked_non_game_roles": (roles - set(GAME_ROLES) - set(READ_ONLY_STAFF_ROLES)) | {"Member"} if "Member" in roles else (roles - set(GAME_ROLES) - set(READ_ONLY_STAFF_ROLES)),
    }


def build_game_hub_overwrites(everyone, game_role, other_game_roles, staff_roles):
    overwrites = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        game_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True),
    }
    for role in other_game_roles:
        overwrites[role] = discord.PermissionOverwrite(view_channel=False, send_messages=False, connect=False, speak=False)
    for role in staff_roles:
        overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True)
    return overwrites


def build_game_hub_channel_policy(game: str, game_roles: list[str] | set[str]):
    return {
        "everyone_view": False,
        "game_role_view": True,
        "other_game_roles_view": False,
        "game": game,
        "other_games": set(game_roles) - {game},
    }

ROLE_COLOURS = {
    "Founder": discord.Colour.from_rgb(232, 184, 74),
    "Co-Founder": discord.Colour.from_rgb(245, 158, 11),
    "Administrator": discord.Colour.from_rgb(240, 93, 94),
    "Operations": discord.Colour.from_rgb(220, 38, 127),
    "Manager": discord.Colour.from_rgb(139, 92, 246),
    "Moderator": discord.Colour.from_rgb(239, 68, 68),
    "Support": discord.Colour.from_rgb(14, 165, 233),
    "Developer": discord.Colour.from_rgb(34, 197, 94),
    "Designer": discord.Colour.from_rgb(236, 72, 153),
    "Content Creator": discord.Colour.from_rgb(251, 146, 60),
    "Client": discord.Colour.from_rgb(245, 158, 11),
    "Verified": discord.Colour.from_rgb(59, 130, 246),
    "Member": discord.Colour.from_rgb(100, 116, 139),
    "Valorant": discord.Colour.from_rgb(239, 68, 68), "Minecraft": discord.Colour.from_rgb(34, 197, 94),
    "GTA V": discord.Colour.from_rgb(234, 179, 8), "CS2": discord.Colour.from_rgb(14, 165, 233),
    "Fortnite": discord.Colour.from_rgb(99, 102, 241), "Roblox": discord.Colour.from_rgb(168, 85, 247),
    "Among Us": discord.Colour.from_rgb(244, 63, 94), "Apex Legends": discord.Colour.from_rgb(249, 115, 22),
    "BGMI / PUBG": discord.Colour.from_rgb(16, 185, 129), "Other Games": discord.Colour.from_rgb(100, 116, 139),
    "Web Developer": discord.Colour.from_rgb(6, 182, 212), "AI / ML": discord.Colour.from_rgb(124, 58, 237),
    "Video Editor": discord.Colour.from_rgb(217, 70, 239), "Esports": discord.Colour.from_rgb(220, 38, 127),
    "Tech": discord.Colour.from_rgb(59, 130, 246), "Art": discord.Colour.from_rgb(236, 72, 153),
    "Music": discord.Colour.from_rgb(168, 85, 247), "Business": discord.Colour.from_rgb(245, 158, 11),
    "Gaming": discord.Colour.from_rgb(99, 102, 241), "Teammates": discord.Colour.from_rgb(34, 197, 94),
    "Competitive": discord.Colour.from_rgb(239, 68, 68), "Events": discord.Colour.from_rgb(245, 158, 11),
    "Networking": discord.Colour.from_rgb(14, 165, 233), "Voice Chat": discord.Colour.from_rgb(168, 85, 247),
    "Announcements": discord.Colour.from_rgb(59, 130, 246), "Event Alerts": discord.Colour.from_rgb(245, 158, 11),
    "Giveaways": discord.Colour.from_rgb(236, 72, 153), "Community Updates": discord.Colour.from_rgb(34, 197, 94),
    "Game Updates": discord.Colour.from_rgb(99, 102, 241),
    "Trial Moderator": discord.Colour.from_rgb(251, 146, 60), "Event Host": discord.Colour.from_rgb(245, 158, 11),
    "QA / Tester": discord.Colour.from_rgb(6, 182, 212), "Partner": discord.Colour.from_rgb(20, 184, 166),
    "Community Helper": discord.Colour.from_rgb(34, 197, 94),
}

GAME_DESCRIPTIONS = {
    "Valorant": "Unlock the Valorant hub.", "Minecraft": "Unlock the Minecraft hub.",
    "GTA V": "Unlock the GTA V hub.", "CS2": "Unlock the CS2 hub.",
    "Fortnite": "Unlock the Fortnite hub.", "Roblox": "Unlock the Roblox hub.",
    "Among Us": "Unlock the Among Us hub.", "Apex Legends": "Unlock the Apex hub.",
    "BGMI / PUBG": "Unlock the BGMI / PUBG hub.", "Other Games": "Unlock the other-games hub.",
}

ONBOARDING_MANAGED_ROLES = [
    "Verified", *GAME_ROLES,
    "Developer", "Designer", "Content Creator", "Web Developer", "AI / ML",
    "Video Editor", "Esports", "Tech", "Art", "Music", "Business",
    "Gaming", "Teammates", "Competitive", "Events", "Networking",
    "Voice Chat", "Announcements", "Event Alerts", "Giveaways", "Community Updates", "Game Updates",
]
ONBOARDING_STEPS = ["profile", "purpose", "interests", "games", "notifications", "finish"]

for _onboarding_role in ONBOARDING_MANAGED_ROLES:
    ROLE_PERMISSION_POLICY.setdefault(_onboarding_role, discord.Permissions.none())
ONBOARDING_EXTRA_ROLES = ["Announcements", "Event Alerts", "Game Updates", "Giveaways", "Community Updates"]
ONBOARDING_ROLE_COLOURS = {
    "Verified": discord.Colour.from_rgb(59, 130, 246),
    "Gaming": discord.Colour.from_rgb(99, 102, 241), "Teammates": discord.Colour.from_rgb(34, 197, 94),
    "Competitive": discord.Colour.from_rgb(239, 68, 68), "Events": discord.Colour.from_rgb(245, 158, 11),
    "Networking": discord.Colour.from_rgb(14, 165, 233), "Voice Chat": discord.Colour.from_rgb(168, 85, 247),
}
GAME_ARTWORK = {
    "Valorant": "https://upload.wikimedia.org/wikipedia/commons/5/5f/Valorant_logo_-_pink_color_version.svg",
    "Minecraft": "https://upload.wikimedia.org/wikipedia/commons/5/51/Minecraft_cover.png",
    "GTA V": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Grand_Theft_Auto_V_logo.svg",
    "CS2": "https://upload.wikimedia.org/wikipedia/commons/6/6c/Counter-Strike_2_logo.svg",
    "Fortnite": "https://upload.wikimedia.org/wikipedia/commons/0/09/FortniteLogo.svg",
    "Roblox": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Roblox_Logo_2022.jpg",
    "Among Us": "https://upload.wikimedia.org/wikipedia/commons/9/9a/Among_Us_logo.svg",
    "Apex Legends": "https://upload.wikimedia.org/wikipedia/commons/d/db/Apex_legends_Logo.svg",
    "BGMI / PUBG": "https://upload.wikimedia.org/wikipedia/commons/0/0c/PUBG_logo.svg",
    "Other Games": "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=1200&q=80",
}
PROFILE_OPTIONS = ["Under 13", "13–15", "16–17", "18–20", "21–24", "25+", "Prefer not to say"]
GENDER_OPTIONS = ["Male", "Female", "Non-binary", "Other", "Prefer not to say"]
REGION_OPTIONS = ["India", "North America", "Europe", "Middle East", "Southeast Asia", "East Asia", "Other"]
PURPOSE_OPTIONS = ["Gaming", "Teammates", "Friends", "Competitive", "Content", "Development", "Design", "Events", "Client / Business", "Browsing"]
INTEREST_OPTIONS = ["Developer", "Web Developer", "AI / ML", "Designer", "Video Editor", "Content Creator", "Music", "Esports", "Tech", "Art", "Business"]
NOTIFICATION_OPTIONS = ["Announcements", "Event Alerts", "Game Updates", "Giveaways", "Community Updates", "None"]


def find_public_text_channel(guild_or_channels, desired_name):
    channels = getattr(guild_or_channels, "text_channels", guild_or_channels)
    exact = next((c for c in channels if c.name == desired_name), None)
    if exact:
        return exact
    desired_tail = desired_name.lstrip("・")
    for channel in channels:
        name = channel.name
        tail = name.split("・・", 1)[-1].lstrip("・")
        if tail == desired_tail:
            return channel
    return None


def channel_policy_for_name(channel_name: str, policies: dict):
    """Find a channel policy by canonical name or emoji-prefixed channel tail."""
    exact = policies.get(channel_name)
    if exact is not None:
        return exact
    tail = channel_name.split("・・", 1)[-1].lstrip("・")
    for policy_name, policy in policies.items():
        if policy_name.lstrip("・") == tail:
            return policy
    return None


PUBLIC_CHANNELS = {
    "welcome": "👋・・𝗪𝗲𝗹𝗰𝗼𝗺𝗲",
    "rules": "📜・・𝗥𝘂𝗹𝗲𝘀",
    "announcements": "📢・・𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁𝘀",
    "roles": "🎭・・𝗖𝗵𝗼𝗼𝘀𝗲・𝗥𝗼𝗹𝗲𝘀",
    "how": "❓・・𝗛𝗼𝘄・𝗜𝘁・𝗪𝗼𝗿𝗸𝘀",
    "faq": "❔・・𝗙𝗔𝗤",
}

WELCOME = """<!-- RUPZHA_WELCOME_PANEL_V2 -->

✦・𝗪𝗘𝗟𝗖𝗢𝗠𝗘・✦

**gaming · creators · friends**

Welcome to **RupZha** — a place to play, meet people, share your work, and build a good community.

╭・𝗦𝗧𝗔𝗥𝗧 𝗛𝗘𝗥𝗘

**01 · 𝗥𝗘𝗔𝗗**
> Read **𝗥𝘂𝗹𝗲𝘀** before jumping in.

**02 · 𝗖𝗛𝗢𝗢𝗦𝗘**
> Use **Community Onboarding** to choose your games and interests, then open your game hub.

**03 · 𝗝𝗢𝗜𝗡 𝗜𝗡**
> Find teammates, chat, share projects, join events, and meet people.

**04 · 𝗛𝗔𝗩𝗘 𝗙𝗨𝗡**
> Keep it respectful, SFW, and chill. Staff have the final say when needed.

╰・𝗥𝗨𝗣𝗭𝗛𝗔

*play • create • connect*"""


RULES = """# 𝗥𝗨𝗣𝗭𝗛𝗔 — 𝗥𝗨𝗟𝗘𝗦

**01 · Respect** — No harassment, hate, threats, or targeted abuse.
**02 · No spam** — No scams, raids, unsolicited advertising, or disruptive promotion.
**03 · Privacy** — Never share private member, client, payment, credential, or project information.
**04 · Right channel** — Keep conversations in the appropriate spaces.
**05 · Gaming** — No cheating, malicious exploits, or attempts to disrupt other players.
**06 · Safety** — No malware, credential theft, or harmful activity.
**07 · Discord** — Follow Discord's Terms of Service and Community Guidelines.

Staff may act when needed to keep Rupzha safe and usable.
"""

HOW = """# 𝗛𝗢𝗪 𝗜𝗧 𝗪𝗢𝗥𝗞𝗦

### 𝗡𝗘𝗪 𝗛𝗘𝗥𝗘?
Read the rules, then open **𝗖𝗵𝗼𝗼𝘀𝗲・𝗥𝗼𝗹𝗲𝘀** and select the games you play.

### 𝗚𝗔𝗠𝗜𝗡𝗚
Each selected game unlocks its own chat, LFG, clips, and voice room.

### 𝗖𝗢𝗠𝗠𝗨𝗡𝗜𝗧𝗬
Use **𝗚𝗲𝗻𝗲𝗿𝗮𝗹**, **𝗚𝗮𝗺𝗶𝗻𝗴・𝗖𝗵𝗮𝘁**, **𝗦𝗵𝗼𝘄𝗰𝗮𝘀𝗲**, and **𝗟𝗙𝗚** to find people and share stuff.

### 𝗥𝗨𝗣𝗭𝗛𝗔 𝗪𝗢𝗥𝗞
Clients and team members have separate private areas. Never post private project details in public channels.
"""

FAQ = """# 𝗙𝗔𝗤

**How do I unlock game channels?**
Use **𝗖𝗵𝗼𝗼𝘀𝗲・𝗥𝗼𝗹𝗲𝘀** and select your games.

**Can I change my games later?**
Yes. Just use the selector again.

**Where do I find teammates?**
Use the community **𝗟𝗙𝗚** channel or the LFG channel inside a game hub.

**Where are private Rupzha projects?**
Inside **𝗖𝗟𝗜𝗘𝗡𝗧 𝗛𝗨𝗕**, **𝗧𝗘𝗔𝗠 𝗛𝗤**, and **𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦**.
"""

def build_onboarding_roles(selections):
    roles = {"Verified"}
    roles.update(selections.get("games", []))
    roles.update(selections.get("interests", []))
    roles.update(selections.get("purpose", []))
    roles.update(selections.get("notifications", []))
    return roles & set(ONBOARDING_MANAGED_ROLES)


async def apply_onboarding(member, selections):
    role_map = {r.name: r for r in member.guild.roles}
    desired = build_onboarding_roles(selections)
    managed = [role_map[name] for name in ONBOARDING_MANAGED_ROLES if name in role_map]
    remove = [r for r in managed if r.name not in desired and r in member.roles]
    add = [role_map[name] for name in desired if name in role_map and role_map[name] not in member.roles]
    if remove:
        await member.remove_roles(*remove, reason="Rupzha onboarding reconciliation")
    if add:
        await member.add_roles(*add, reason="Rupzha onboarding")
    return sorted(desired)


class OnboardingEntryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Start Onboarding", style=discord.ButtonStyle.primary, custom_id="rupzha:onboarding:start")
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=discord.Embed(title="𝗥𝗨𝗣𝗭𝗛𝗔 𝗢𝗡𝗕𝗢𝗔𝗥𝗗𝗜𝗡𝗚", description="Let's set up your profile. Your answers stay private to you and are not posted in the server."),
            view=OnboardingView(), ephemeral=True,
        )


class OnboardingSelect(discord.ui.Select):
    def __init__(self, key, placeholder, options, max_values=1):
        self.key = key
        super().__init__(
            custom_id=f"rupzha:onboarding:{key}",
            placeholder=placeholder,
            min_values=1,
            max_values=max_values,
            options=[discord.SelectOption(label=o, value=o) for o in options],
        )

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if not isinstance(view, OnboardingView):
            return
        view.data[self.key] = list(self.values)
        await interaction.response.edit_message(embed=view.embed_for_current_step(), view=view)


class OnboardingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=900)
        self.step = 0
        self.data = {"profile": [], "gender": [], "region": [], "purpose": [], "interests": [], "games": [], "notifications": []}
        self.refresh_items()

    def embed_for_current_step(self):
        titles = ["𝗔𝗕𝗢𝗨𝗧 𝗬𝗢𝗨", "𝗪𝗛𝗔𝗧 𝗕𝗥𝗜𝗡𝗚𝗦 𝗬𝗢𝗨 𝗛𝗘𝗥𝗘?", "𝗦𝗞𝗜𝗟𝗟𝗦 & 𝗜𝗡𝗧𝗘𝗥𝗘𝗦𝗧𝗦", "𝗬𝗢𝗨𝗥 𝗚𝗔𝗠𝗘𝗦", "𝗡𝗢𝗧𝗜𝗙𝗜𝗖𝗔𝗧𝗜𝗢𝗡𝗦", "𝗙𝗜𝗡𝗜𝗦𝗛"]
        descriptions = [
            "Age range is used only for community context. Gender is optional. Region is broad and never used for permissions.",
            "Pick what you want from RupZha. Choose everything that fits.",
            "Tell us what you do or are interested in.",
            "Pick every game you play. Each selected game unlocks its hub. Game artwork is shown below.",
            "Choose the updates you actually want.",
            "Review complete. Finish to receive your safe community roles and unlock your selected hubs.",
        ]
        embed = discord.Embed(title=f"{titles[self.step]} · {self.step + 1}/6", description=descriptions[self.step])
        if self.step == 3:
            chosen = self.data["games"] or ["None yet"]
            embed.add_field(name="Selected", value=", ".join(chosen), inline=False)
            embed.set_image(url=GAME_ARTWORK.get(chosen[0]) if chosen[0] in GAME_ARTWORK else GAME_ARTWORK["Other Games"])
        if self.step == 5:
            for key, label in (("profile", "Age"), ("gender", "Gender"), ("region", "Region"), ("purpose", "Purpose"), ("interests", "Interests"), ("games", "Games"), ("notifications", "Notifications")):
                value = self.data[key] or ["Not selected"]
                embed.add_field(name=label, value=", ".join(value), inline=False)
        return embed

    def refresh_items(self):
        self.clear_items()
        configs = [
            [("profile", "𝗔𝗴𝗲 𝗿𝗮𝗻𝗴𝗲", PROFILE_OPTIONS, 1), ("gender", "𝗚𝗲𝗻𝗱𝗲𝗿 (optional)", GENDER_OPTIONS, 1), ("region", "𝗕𝗿𝗼𝗮𝗱 𝗿𝗲𝗴𝗶𝗼𝗻", REGION_OPTIONS, 1)],
            [("purpose", "𝗖𝗵𝗼𝗼𝘀𝗲 𝘄𝗵𝗮𝘁 𝘆𝗼𝘂'𝗿𝗲 𝗵𝗲𝗿𝗲 𝗳𝗼𝗿", PURPOSE_OPTIONS, 10)],
            [("interests", "𝗦𝗸𝗶𝗹𝗹𝘀 & 𝗶𝗻𝘁𝗲𝗿𝗲𝘀𝘁𝘀", INTEREST_OPTIONS, 10)],
            [("games", "𝗖𝗵𝗼𝗼𝘀𝗲 𝘆𝗼𝘂𝗿 𝗴𝗮𝗺𝗲𝘀", GAME_ROLES, len(GAME_ROLES))],
            [("notifications", "𝗡𝗼𝘁𝗶𝗳𝗶𝗰𝗮𝘁𝗶𝗼𝗻𝘀", NOTIFICATION_OPTIONS, 6)],
            [],
        ]
        for key, placeholder, options, maximum in configs[self.step]:
            current = set(self.data.get(key, []))
            select = OnboardingSelect(key, placeholder, options, maximum)
            self.add_item(select)
        if self.step > 0:
            back = discord.ui.Button(label="Back", style=discord.ButtonStyle.secondary, custom_id="rupzha:onboarding:back")
            back.callback = self.back
            self.add_item(back)
        if self.step < 5:
            nxt = discord.ui.Button(label="Next", style=discord.ButtonStyle.primary, custom_id="rupzha:onboarding:next")
            nxt.callback = self.next
            self.add_item(nxt)
        else:
            finish = discord.ui.Button(label="Finish Setup", style=discord.ButtonStyle.success, custom_id="rupzha:onboarding:finish")
            finish.callback = self.finish
            self.add_item(finish)

    async def next(self, interaction):
        if self.step == 0 and (not self.data["profile"] or not self.data["region"]):
            await interaction.response.send_message("Pick your age range and broad region first. Gender is optional.", ephemeral=True)
            return
        if self.step == 3 and not self.data["games"]:
            await interaction.response.send_message("Pick at least one game, or choose Other Games.", ephemeral=True)
            return
        self.step += 1
        self.refresh_items()
        await interaction.response.edit_message(embed=self.embed_for_current_step(), view=self)

    async def back(self, interaction):
        self.step -= 1
        self.refresh_items()
        await interaction.response.edit_message(embed=self.embed_for_current_step(), view=self)

    async def finish(self, interaction):
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("This onboarding only works inside RupZha.", ephemeral=True)
            return
        try:
            selected = await apply_onboarding(interaction.user, self.data)
            await interaction.response.edit_message(embed=discord.Embed(title="𝗢𝗡𝗕𝗢𝗔𝗥𝗗𝗜𝗡𝗚 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘", description="You're verified. Your selected community, interest, notification, and game roles are now active.\n\nProfile answers were kept private."), view=None)
            print(f"ONBOARDING COMPLETE · {interaction.user.id} · {', '.join(selected)}")
        except discord.Forbidden:
            await interaction.response.send_message("I can't manage one of the onboarding roles. Please contact staff.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("Discord rejected the role update. Try again in a moment.", ephemeral=True)


WELCOME_PANEL_MARKER = "RUPZHA_WELCOME_PANEL_V2"


def is_static_welcome_message(message):
    """Return True only for the current persistent generic welcome board."""
    embeds = getattr(message, "embeds", None) or []
    if not embeds:
        return False
    embed = embeds[0]
    footer = getattr(embed, "footer", None)
    footer_text = getattr(footer, "text", "") if footer else ""
    if WELCOME_PANEL_MARKER in footer_text:
        return True
    return getattr(embed, "title", None) in {"✦・𝗪𝗘𝗟𝗖𝗢𝗠𝗘・✦", "✦ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗨𝗣𝗭𝗛𝗔 ✦"} and not getattr(embed, "thumbnail", None)


def is_legacy_welcome_message(message):
    """Identify old RupZha welcome panels so the channel can be cleaned once."""
    embeds = getattr(message, "embeds", None) or []
    if not embeds:
        return False
    title = getattr(embeds[0], "title", None) or ""
    return title in {"✦ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗨𝗣𝗭𝗛𝗔 ✦", "𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗨𝗣𝗭𝗛𝗔"}

def build_static_welcome_embed():
    embed = discord.Embed(
        title="✦・𝗪𝗘𝗟𝗖𝗢𝗠𝗘・✦",
        description=(
            "**gaming · creators · friends**\n\n"
            "Welcome to **RupZha** — a place to play, meet people, share your work, and build a good community.\n\n"
            "**01 · 𝗥𝗘𝗔𝗗** → Rules\n"
            "**02 · 𝗖𝗛𝗢𝗢𝗦𝗘** → Pick your games and interests\n"
            "**03 · 𝗝𝗢𝗜𝗡 𝗜𝗡** → Chat, find teammates, share projects, join events\n"
            "**04 · 𝗛𝗔𝗩𝗘 𝗙𝗨𝗡** → Keep it respectful, SFW, and chill"
        ),
        color=discord.Color(0xFF1F3D),
    )
    embed.set_image(url="attachment://rupzha-welcome.gif")
    embed.set_footer(text=f"RupZha · play • create • connect · {WELCOME_PANEL_MARKER}")
    return embed


def welcome_panel_file():
    if not WELCOME_GIF_PATH.is_file():
        raise FileNotFoundError(f"Missing welcome asset: {WELCOME_GIF_PATH}")
    return discord.File(WELCOME_GIF_PATH, filename="rupzha-welcome.gif")


async def ensure_welcome_panel(channel):
    try:
        canonical = None
        async for message in channel.history(limit=100):
            if is_legacy_welcome_message(message):
                await message.delete()
                continue
            if not is_static_welcome_message(message):
                continue
            image_url = message.embeds[0].image.url if message.embeds else None
            has_graphic = any(getattr(attachment, "filename", "") == "rupzha-welcome.gif" for attachment in message.attachments)
            is_graphical_embed = bool(image_url and (image_url == "attachment://rupzha-welcome.gif" or "rupzha-welcome.gif" in image_url))
            if not has_graphic and not is_graphical_embed:
                await message.delete()
                continue
            if canonical is None:
                canonical = message
                if not message.pinned:
                    await message.pin(reason="RupZha canonical welcome board")
            else:
                await message.delete()
        if canonical is not None:
            return canonical
        message = await channel.send(embed=build_static_welcome_embed(), file=welcome_panel_file())
        await message.pin(reason="RupZha canonical welcome board")
        return message
    except (discord.Forbidden, discord.HTTPException) as exc:
        print(f"WARN welcome panel #{channel.name}: {exc}")
        return None

async def seed(channel, content):
    try:
        async for message in channel.history(limit=20):
            if message.author == bot.user:
                if message.content != content:
                    await message.edit(content=content)
                return
        await channel.send(content)
    except (discord.Forbidden, discord.HTTPException) as exc:
        print(f"WARN seed #{channel.name}: {exc}")

def harden_third_party_bot_permissions(permissions: discord.Permissions) -> discord.Permissions:
    """Remove server-wide escalation from a utility bot role while preserving harmless capabilities."""
    hardened = discord.Permissions(permissions.value)
    for attr in (
        "administrator", "manage_guild", "manage_roles", "manage_channels",
        "manage_webhooks", "kick_members", "ban_members", "moderate_members",
        "mention_everyone",
    ):
        setattr(hardened, attr, False)
    return hardened


def permissions_for_third_party_bot_role(role_name: str, permissions: discord.Permissions) -> discord.Permissions:
    """Return safe permissions for bots that must be restricted to dedicated channels."""
    if role_name in DEDICATED_BOT_CHANNELS:
        return harden_third_party_bot_permissions(permissions)
    return discord.Permissions(permissions.value)


def harden_unapproved_role_permissions(permissions: discord.Permissions) -> discord.Permissions:
    """Remove unapproved server-wide powers while preserving ordinary channel access."""
    hardened = discord.Permissions(permissions.value)
    for attr in (
        "administrator", "manage_guild", "manage_roles", "manage_channels",
        "manage_webhooks", "kick_members", "ban_members", "moderate_members",
        "mention_everyone", "manage_messages",
    ):
        setattr(hardened, attr, False)
    return hardened


async def clear_shared_member_role_overwrites(guild):
    """Remove stale Member-role overrides while preserving per-user bot overrides.

    Public chat should inherit @everyone permissions. Private categories remain private
    because their @everyone overwrite denies view_channel, and game hubs remain locked
    because their @everyone overwrite also denies view_channel.
    """
    member_role = discord.utils.get(guild.roles, name="Member")
    if member_role is None:
        return 0

    removed = 0
    for channel in list(guild.channels):
        if channel.overwrites_for(member_role) == discord.PermissionOverwrite():
            continue
        try:
            await channel.set_permissions(
                member_role,
                overwrite=None,
                reason="RupZha permission repair: restore inherited Member role access",
            )
            removed += 1
        except discord.HTTPException as exc:
            print(f"WARN Member role overwrite cleanup {channel.name}: {exc}")
    if removed:
        print(f"MEMBER ROLE PERMISSION REPAIR · removed {removed} stale channel overrides")
    return removed


async def ensure_ticket_rooms_category(guild):
    """Return a private category for actual ticket rooms, separate from the public panel."""
    category = discord.utils.get(guild.categories, name=TICKET_ROOMS_CATEGORY)
    if category:
        return category
    staff_roles = [
        role for role in guild.roles
        if role.name in {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator", "Support"}
    ]
    overwrites = build_ticket_category_overwrites(guild.default_role, staff_roles)
    category = await guild.create_category(
        TICKET_ROOMS_CATEGORY,
        overwrites=overwrites,
        reason="RupZha tickets: separate private ticket rooms from the public ticket panel",
    )
    print(f"TICKET ROOMS CATEGORY READY · {category.name}")
    return category


def ticket_panel_has_marker(message, marker: str) -> bool:
    if marker in (getattr(message, "content", "") or ""):
        return True
    for embed in getattr(message, "embeds", None) or []:
        footer = getattr(embed, "footer", None)
        footer_text = getattr(footer, "text", None) or ""
        if marker in footer_text:
            return True
    return False


async def ensure_ticket_archive_category(guild):
    category = discord.utils.get(guild.categories, name=TICKET_ARCHIVE_CATEGORY)
    if category:
        return category
    staff_roles = [
        role for role in guild.roles
        if role.name in {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator", "Support"}
    ]
    overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
    for role in staff_roles:
        overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True)
    category = await guild.create_category(
        TICKET_ARCHIVE_CATEGORY,
        overwrites=overwrites,
        reason="RupZha tickets: private closed-ticket archive",
    )
    print(f"TICKET ARCHIVE CATEGORY READY · {category.name}")
    return category


async def ensure_ticket_panel(guild):
    """Keep one canonical public ticket panel with persistent RupZha buttons."""
    channel = find_public_text_channel(guild, "・𝗧𝗶𝗰𝗸𝗲𝘁・𝗣𝗮𝗻𝗲𝗹")
    if channel is None:
        return None
    marker = "RUPZHA_TICKET_PANEL_V1"
    canonical = None
    try:
        async for message in channel.history(limit=100):
            if ticket_panel_has_marker(message, marker):
                if canonical is None:
                    canonical = message
                else:
                    await message.delete(reason="RupZha ticket panel deduplication")
        embed = build_ticket_panel_embed()
        embed.set_footer(text=marker)
        view = TicketPanelView()
        if canonical is None:
            canonical = await channel.send(embed=embed, view=view)
            await canonical.pin()
            print(f"TICKET PANEL CREATED · #{channel.name} · {canonical.id}")
        else:
            await canonical.edit(embed=embed, view=view)
            if not canonical.pinned:
                await canonical.pin()
            print(f"TICKET PANEL REPAIRED · #{channel.name} · {canonical.id}")
        return canonical
    except (discord.Forbidden, discord.HTTPException) as exc:
        print(f"WARN ticket panel #{channel.name}: {exc}")
        return None


async def setup_server(guild):
    roles = {r.name: r for r in guild.roles}
    me = guild.me
    if not me:
        print("WARN: bot member unavailable")
        return

    # Reconcile the canonical public ticket panel every startup; the function
    # deduplicates its own panel message and never creates extra ticket rooms.
    await ensure_ticket_panel(guild)
    try:
        await ensure_ticket_rooms_category(guild)
        await ensure_ticket_archive_category(guild)
    except (discord.Forbidden, discord.HTTPException) as exc:
        print(f"WARN ticket categories: {exc}")
    for row in db.fetchall(
        "SELECT ticket_id, opener_id, status FROM tickets WHERE guild_id = ? AND status IN ('open', 'closed', 'archived') ORDER BY rowid DESC LIMIT 500",
        (guild.id,),
    ):
        if row["status"] == "open":
            bot.add_view(TicketControlsView(row["ticket_id"]))
        elif not db.fetchone("SELECT feedback_id FROM ticket_feedback WHERE ticket_id = ?", (row["ticket_id"],)):
            bot.add_view(TicketFeedbackView(row["ticket_id"], row["opener_id"]))

    # Repair stale shared-role denies before reconciling any other channel permissions.
    await clear_shared_member_role_overwrites(guild)

    # Create only purposeful optional/notification roles; optional roles are never auto-assigned.
    for role_name in OPTIONAL_ROLE_POLICY:
        if role_name not in roles:
            try:
                await guild.create_role(name=role_name, permissions=discord.Permissions.none(), colour=ROLE_COLOURS[role_name], reason="Rupzha optional role setup")
            except discord.HTTPException as exc:
                print(f"WARN optional role {role_name}: {exc}")
    roles = {r.name: r for r in guild.roles}

    # Keep the Start Here funnel complete: the personalized welcome references
    # Choose Roles, so never leave that canonical channel missing.
    start_here = discord.utils.get(guild.categories, name="╭・𝗦𝗧𝗔𝗥𝗧 𝗛𝗘𝗥𝗘")
    if start_here:
        for channel_name in PUBLIC_CHANNELS.values():
            existing = discord.utils.get(guild.text_channels, name=channel_name)
            if existing is None:
                try:
                    await guild.create_text_channel(
                        channel_name,
                        category=start_here,
                        reason="RupZha: restore canonical Start Here channel",
                    )
                    print(f"PUBLIC CHANNEL RESTORED · #{channel_name}")
                except discord.HTTPException as exc:
                    print(f"WARN public channel {channel_name}: {exc}")

    # Create only the small set of notification roles; game and interest roles already exist.
    # Never create or elevate staff/client roles here.
    for role_name in ONBOARDING_EXTRA_ROLES:
        if role_name not in roles:
            try:
                await guild.create_role(
                    name=role_name,
                    permissions=discord.Permissions.none(),
                    colour=ONBOARDING_ROLE_COLOURS.get(role_name, discord.Colour.default()),
                    reason="Rupzha onboarding role setup",
                )
            except discord.HTTPException as exc:
                print(f"WARN onboarding role {role_name}: {exc}")
    roles = {r.name: r for r in guild.roles}

    # Diagnose the custom Rupzha Bot role explicitly before security reconciliation.
    rupzha_bot_role = discord.utils.get(guild.roles, name="Rupzha Bot")
    if rupzha_bot_role is not None:
        print(
            f"RUPZHA BOT ROLE · managed={rupzha_bot_role.managed} position={rupzha_bot_role.position} "
            f"bot_top={me.top_role.position} administrator={rupzha_bot_role.permissions.administrator} "
            f"manage_roles={rupzha_bot_role.permissions.manage_roles} manage_channels={rupzha_bot_role.permissions.manage_channels} "
            f"manage_messages={rupzha_bot_role.permissions.manage_messages}"
        )

    # The bot only manages roles below its own role. Role ordering is intentionally not
    # mutated automatically here; Discord's role UI is safer for the final staff hierarchy.
    # All functional roles remain below the bot role.

    # Harden unmanaged bot roles without touching managed integration roles or our explicit staff policy.
    # Preserve benign permissions (e.g. Manage Messages) and remove only server-wide escalation.
    bot_member_names = {m.name for m in guild.members if m.bot}
    protected_custom_roles = set(ROLE_PERMISSION_POLICY)
    for role in guild.roles:
        if role.is_default() or role.managed or role >= me.top_role or role.name in protected_custom_roles:
            continue
        if role.name in bot_member_names:
            hardened = permissions_for_third_party_bot_role(role.name, role.permissions)
            if hardened.value != role.permissions.value:
                try:
                    await role.edit(permissions=hardened, reason="Rupzha bot role safety: remove server-wide escalation")
                    print(f"BOT ROLE HARDENED {role.name}")
                except discord.HTTPException as exc:
                    print(f"WARN bot role safety {role.name}: {exc}")
        else:
            hardened = harden_unapproved_role_permissions(role.permissions)
            if hardened.value != role.permissions.value:
                try:
                    await role.edit(permissions=hardened, reason="Rupzha role governance: strip unapproved server-wide powers")
                    print(f"UNAPPROVED ROLE HARDENED {role.name}")
                except discord.HTTPException as exc:
                    print(f"WARN unapproved role safety {role.name}: {exc}")

    # Strict role permissions: only the explicitly privileged staff roles get power.
    for name, perms in ROLE_PERMISSION_POLICY.items():
        role = roles.get(name)
        if role and role < me.top_role:
            expected_colour = ROLE_COLOURS.get(name, role.colour)
            if role.permissions.value == perms.value and role.colour.value == expected_colour.value:
                continue
            try:
                await role.edit(permissions=perms, colour=expected_colour, reason="Rupzha role permissions")
            except discord.HTTPException as exc:
                print(f"WARN role {name}: {exc}")

    if os.getenv("RUPZHA_ROLE_ONLY") == "1":
        print("ROLE-ONLY RECONCILE COMPLETE")
        return

    # Game hubs stay hidden until a member selects the matching game role.
    for game in GAME_ROLES:
        role = roles.get(game)
        if not role:
            continue
        category = discord.utils.get(guild.categories, name=f"╭・𝗚𝗔𝗠𝗘・{game.upper()}")
        if not category:
            category = discord.utils.find(lambda c: game.lower() in c.name.lower() and "𝗚𝗔𝗠𝗘" in c.name, guild.categories)
        if category:
            other_game_roles = {r for r in roles.values() if r.name in GAME_ROLES and r.name != game}
            staff_roles = {roles[name] for name in ("Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator") if roles.get(name)}
            overwrites = build_game_hub_overwrites(guild.default_role, role, other_game_roles, staff_roles)
            try:
                if category.overwrites != overwrites:
                    await category.edit(overwrites=overwrites, reason="Rupzha game hub permissions")
                for child in category.channels:
                    if isinstance(child, (discord.TextChannel, discord.VoiceChannel, discord.StageChannel)) and child.overwrites != overwrites:
                        await child.edit(overwrites=overwrites, reason="Rupzha game channel permissions")
            except discord.HTTPException as exc:
                print(f"WARN game hub {game}: {exc}")

    # Reconcile utility bot command channels to one canonical channel per bot.
    bot_command_category_name = "╭・𝗕𝗢𝗧・𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦"
    bot_command_category = discord.utils.get(guild.categories, name=bot_command_category_name)
    if not bot_command_category:
        try:
            bot_command_category = await guild.create_category(bot_command_category_name, reason="Rupzha third-party bot command isolation")
        except discord.HTTPException as exc:
            print(f"WARN bot command category: {exc}")
            bot_command_category = None
    if bot_command_category:
        # Clean up the previous over-expanded bot layout. Keep only the three
        # intentional member-facing channels and consolidate duplicate bot
        # categories so the server cannot grow extra rooms on every restart.
        bot_categories = [c for c in guild.categories if c.name == bot_command_category_name]
        keep_names = {BOT_COMMAND_CHANNEL_NAME, *DEDICATED_BOT_CHANNELS.values()}
        for category in bot_categories:
            for channel in list(category.text_channels):
                if channel.name not in keep_names:
                    try:
                        await channel.delete(reason="Rupzha cleanup: remove unnecessary bot channel")
                        print(f"BOT CHANNEL CLEANED · #{channel.name}")
                    except discord.HTTPException as exc:
                        print(f"WARN bot cleanup {channel.name}: {exc}")
        for category in bot_categories:
            if category.id != bot_command_category.id and not category.channels:
                try:
                    await category.delete(reason="Rupzha cleanup: remove duplicate bot category")
                    print(f"BOT CATEGORY CLEANED · {category.id}")
                except discord.HTTPException as exc:
                    print(f"WARN bot category cleanup: {exc}")

        # One shared public command room for all member-facing utility bots.
        # Do not create inside a per-bot loop: Discord.py caches category children,
        # which previously caused one fresh channel per bot during a restart.
        shared_name = BOT_COMMAND_CHANNEL_NAME
        shared_candidates = [c for c in guild.text_channels if c.name == shared_name]
        shared = shared_candidates[0] if shared_candidates else None
        if shared is None:
            try:
                shared = await guild.create_text_channel(
                    shared_name,
                    category=bot_command_category,
                    reason="Rupzha: canonical shared utility bot command channel",
                )
                print(f"BOT CHANNEL CREATED · #{shared.name}")
            except discord.HTTPException as exc:
                print(f"WARN shared bot channel: {exc}")
        elif shared.category != bot_command_category:
            try:
                await shared.edit(
                    category=bot_command_category,
                    sync_permissions=True,
                    reason="Rupzha: canonical shared utility bot command channel",
                )
                print(f"BOT CHANNEL ADOPTED · #{shared.name}")
            except discord.HTTPException as exc:
                print(f"WARN shared bot channel adopt: {exc}")

        # Collapse any duplicate shared rooms, preserving history by moving it
        # into the private bot-log area rather than leaving sidebar clutter.
        if shared is not None:
            logs_category = discord.utils.get(guild.categories, name="╭・𝗕𝗢𝗧・𝗟𝗢𝗚𝗦")
            for duplicate in list(shared_candidates[1:]):
                try:
                    has_history = False
                    async for _ in duplicate.history(limit=1):
                        has_history = True
                        break
                    if has_history and logs_category:
                        await duplicate.edit(
                            name=f"🗄️・・𝗟𝗲𝗴𝗮𝗰𝘆・{duplicate.id % 10000}",
                            category=logs_category,
                            reason="RupZha: preserve duplicate bot command history privately",
                        )
                        print(f"BOT HISTORY MOVE · {duplicate.id}")
                    else:
                        await duplicate.delete(reason="RupZha: remove duplicate shared bot command channel")
                        print(f"BOT CHANNEL DELETED · {duplicate.id}")
                except discord.HTTPException as exc:
                    print(f"WARN shared bot dedupe {duplicate.id}: {exc}")

        # Reconcile the three member-facing utility bots into their own canonical
        # public channels. This is intentionally separate from the shared utility
        # room so OwO, Pokétwo, and Koya never compete for one command stream.
        dedicated_channels = {}
        logs_category = discord.utils.get(guild.categories, name="╭・𝗕𝗢𝗧・𝗟𝗢𝗚𝗦")
        for bot_name, canonical_name in DEDICATED_BOT_CHANNELS.items():
            candidates = [c for c in guild.text_channels if c.name == canonical_name]
            aliases = BOT_CHANNEL_ALIASES.get(bot_name, set())
            alias_candidates = [c for c in guild.text_channels if c.name in aliases and c.name != canonical_name]
            channel = candidates[0] if candidates else (alias_candidates[0] if alias_candidates else None)
            if channel is None:
                try:
                    channel = await guild.create_text_channel(
                        canonical_name,
                        category=bot_command_category,
                        reason=f"RupZha: dedicated {bot_name} command channel",
                    )
                    print(f"DEDICATED BOT CHANNEL CREATED · {bot_name} · #{canonical_name}")
                except discord.HTTPException as exc:
                    print(f"WARN dedicated bot channel {bot_name}: {exc}")
                    continue
            elif channel.name != canonical_name:
                try:
                    await channel.edit(
                        name=canonical_name,
                        category=bot_command_category,
                        sync_permissions=True,
                        reason=f"RupZha: canonicalize dedicated {bot_name} command channel",
                    )
                    print(f"DEDICATED BOT CHANNEL ADOPTED · {bot_name} · #{canonical_name}")
                except discord.HTTPException as exc:
                    print(f"WARN dedicated bot channel adopt {bot_name}: {exc}")
            elif channel.category != bot_command_category:
                try:
                    await channel.edit(
                        category=bot_command_category,
                        sync_permissions=True,
                        reason=f"RupZha: move dedicated {bot_name} command channel",
                    )
                except discord.HTTPException as exc:
                    print(f"WARN dedicated bot category move {bot_name}: {exc}")
            dedicated_channels[bot_name] = channel

            # Preserve duplicate/legacy rooms instead of deleting history. Empty
            # duplicates are safe to remove; populated duplicates are moved to the
            # private bot-log category so the public command area stays clean.
            duplicate_channels = [c for c in (candidates + alias_candidates) if c.id != channel.id]
            for duplicate in duplicate_channels:
                try:
                    has_history = False
                    async for _ in duplicate.history(limit=1):
                        has_history = True
                        break
                    if has_history and logs_category:
                        await duplicate.edit(
                            name=f"🗄️・・𝗟𝗲𝗴𝗮𝗰𝘆・{duplicate.id % 10000}",
                            category=logs_category,
                            reason=f"RupZha: preserve duplicate {bot_name} command history",
                        )
                    else:
                        await duplicate.delete(reason=f"RupZha: remove duplicate {bot_name} command channel")
                except discord.HTTPException as exc:
                    print(f"WARN dedicated bot duplicate {bot_name} #{duplicate.name}: {exc}")

        # Each dedicated bot role is explicitly denied in the other dedicated
        # channels and explicitly allowed in its own channel. @everyone remains
        # public, so members can still see and use the channels normally.
        dedicated_roles = {name: roles.get(name) for name in DEDICATED_BOT_CHANNELS}
        if shared is not None:
            for bot_name, role in dedicated_roles.items():
                if role is None:
                    continue
                try:
                    await shared.set_permissions(
                        role,
                        view_channel=False,
                        read_message_history=False,
                        send_messages=False,
                        send_messages_in_threads=False,
                        create_public_threads=False,
                        create_private_threads=False,
                        use_application_commands=False,
                        add_reactions=False,
                        reason=f"RupZha dedicated bot isolation: {bot_name} leaves shared utility channel",
                    )
                except discord.HTTPException as exc:
                    print(f"WARN shared bot permission {bot_name}: {exc}")

        for bot_name, channel in dedicated_channels.items():
            for other_name, role in dedicated_roles.items():
                if role is None:
                    continue
                allowed = bot_name == other_name
                try:
                    await channel.set_permissions(
                        role,
                        view_channel=allowed,
                        read_message_history=allowed,
                        send_messages=allowed,
                        send_messages_in_threads=allowed,
                        create_public_threads=allowed,
                        create_private_threads=False,
                        use_application_commands=allowed,
                        add_reactions=allowed,
                        reason=f"RupZha dedicated bot isolation: {bot_name}",
                    )
                except discord.HTTPException as exc:
                    print(f"WARN dedicated bot permission {other_name} -> {channel.name}: {exc}")

        # Remove any legacy per-bot command rooms left elsewhere in the guild.
        # The canonical dedicated channels above are intentionally exempt.
        legacy_names = {alias for aliases in BOT_CHANNEL_ALIASES.values() for alias in aliases}
        legacy_names |= {"🤖・・𝗢𝘄𝗢", "🎮・・𝗣𝗼𝗸𝗲𝘁𝘄𝗼", "🌸・・𝗞𝗼𝘆𝗮"}
        for channel in list(guild.text_channels):
            if channel.name in {shared_name, *DEDICATED_BOT_CHANNELS.values()} or channel.name.startswith("🗄️・・"):
                continue
            if channel.name in legacy_names:
                try:
                    has_history = False
                    async for _ in channel.history(limit=1):
                        has_history = True
                        break
                    if has_history:
                        logs_category = discord.utils.get(guild.categories, name="╭・𝗕𝗢𝗧・𝗟𝗢𝗚𝗦")
                        if logs_category:
                            await channel.edit(
                                name=f"🗄️・・𝗟𝗲𝗴𝗮𝗰𝘆・{channel.id % 10000}",
                                category=logs_category,
                                reason="RupZha: preserve legacy bot history privately",
                            )
                    else:
                        await channel.delete(reason="RupZha: remove obsolete bot command channel")
                    print(f"BOT LEGACY CLEANED · #{channel.name}")
                except discord.HTTPException as exc:
                    print(f"WARN legacy bot cleanup {channel.name}: {exc}")

    # Keep actual private ticket rooms separate from the member-facing ticket panel.
    try:
        await ensure_ticket_rooms_category(guild)
    except discord.HTTPException as exc:
        print(f"WARN ticket rooms category: {exc}")

    # Apply the same strict access model to private workspace and bot sections.
    for category_name, allowed in CATEGORY_ACCESS_POLICY.items():
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            continue
        overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        for role_name in allowed:
            role = roles.get(role_name)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True)
        try:
            if category.overwrites != overwrites:
                await category.edit(overwrites=overwrites, reason="Rupzha strict role access")
        except discord.HTTPException as exc:
            print(f"WARN restricted category {category_name}: {exc}")

    # Child-channel locks make public documentation read-only and sensitive bot logs write-only.
    # Utility-bot isolation is repaired separately and is deliberately NOT rewritten across
    # every channel on every startup; that old approach caused hundreds of permission PUTs
    # and Discord 429s. Category/channel permissions are persistent Discord state.
    for channel in guild.text_channels:
        policy = channel_policy_for_name(channel.name, CHANNEL_LOCK_POLICY)
        if not policy:
            continue
        mode = policy["mode"]
        try:
            overwrites = dict(channel.overwrites)
            if mode == "public_read_only":
                overwrites[guild.default_role] = discord.PermissionOverwrite(view_channel=True, send_messages=False, add_reactions=False, create_public_threads=False, create_private_threads=False, send_messages_in_threads=False)
                for role_name in READ_ONLY_STAFF_ROLES:
                    role = roles.get(role_name)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
            elif mode == "public_read_only_bot_write":
                overwrites[guild.default_role] = discord.PermissionOverwrite(view_channel=True, send_messages=False, add_reactions=False, create_public_threads=False, create_private_threads=False, send_messages_in_threads=False)
                for role_name in READ_ONLY_STAFF_ROLES:
                    role = roles.get(role_name)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
                for bot_role_name in policy.get("bot_roles", []):
                    role = roles.get(bot_role_name)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, embed_links=True, attach_files=True, manage_messages=True)
            elif mode == "client_read_only":
                overwrites[guild.default_role] = discord.PermissionOverwrite(view_channel=False)
                for role_name in CATEGORY_ACCESS_POLICY["╭・𝗖𝗟𝗜𝗘𝗡𝗧 𝗛𝗨𝗕"]:
                    role = roles.get(role_name)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True)
                for role_name in READ_ONLY_STAFF_ROLES:
                    role = roles.get(role_name)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
            elif mode == "restricted_read_only":
                overwrites[guild.default_role] = discord.PermissionOverwrite(view_channel=False)
                for role_name in CATEGORY_ACCESS_POLICY["╭・𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦"] | READ_ONLY_STAFF_ROLES:
                    role = roles.get(role_name)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
            elif mode == "restricted_bot_write":
                overwrites[guild.default_role] = discord.PermissionOverwrite(view_channel=False)
                for role_name in CATEGORY_ACCESS_POLICY.get(channel.category.name if channel.category else "", set()) | READ_ONLY_STAFF_ROLES:
                    role = roles.get(role_name)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
                for bot_role_name in policy.get("bot_roles", []):
                    role = roles.get(bot_role_name)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, embed_links=True, attach_files=True, manage_messages=True)
            await channel.edit(overwrites=overwrites, reason="Rupzha channel lock policy")
        except discord.HTTPException as exc:
            print(f"WARN channel lock {channel.name}: {exc}")

    # Utility-bot command isolation is intentionally not reconciled here.
    # A one-time repair establishes the persistent Discord overwrites; startup
    # must remain cheap and idempotent instead of rewriting 100+ channels.

    start = discord.utils.get(guild.categories, name="╭・𝗦𝗧𝗔𝗥𝗧 𝗛𝗘𝗥𝗘")
    if not start:
        print("WARN: START HERE category missing")
        return

    channels = {c.name: c for c in start.text_channels}
    for logical_name in PUBLIC_CHANNELS.values():
        channel = find_public_text_channel(start, logical_name)
        if channel:
            channels.setdefault(logical_name, channel)
    content = {
        PUBLIC_CHANNELS["welcome"]: WELCOME,
        PUBLIC_CHANNELS["rules"]: RULES,
        PUBLIC_CHANNELS["how"]: HOW,
        PUBLIC_CHANNELS["faq"]: FAQ,
        PUBLIC_CHANNELS["announcements"]: "# 𝗥𝗨𝗣𝗭𝗛𝗔 𝗔𝗡𝗡𝗢𝗨𝗡𝗖𝗘𝗠𝗘𝗡𝗧𝗦\n\nOfficial server news, events, updates, and important notices will appear here.",
    }
    for name, text in content.items():
        if name in channels and name != PUBLIC_CHANNELS["welcome"]:
            await seed(channels[name], text)

    # The welcome board is repaired exactly once in on_ready before this
    # reconciliation pass. Keeping it out of setup_server prevents startup
    # races that could create a second pinned welcome board.
    # Native Discord Community Onboarding is the only onboarding entry point.
    # Do not seed a post-join bot onboarding panel; it would duplicate/conflict with the pre-join flow.

    # Live audit: resolve canonical channel names by their emoji-insensitive tail.
    # discord.py stores the full display name, while CHANNEL_LOCK_POLICY stores
    # the stable tail. Comparing the raw strings made the old audit report
    # false "missing" failures for perfectly valid channels.
    live_failures = []
    for name, expected in ROLE_PERMISSION_POLICY.items():
        role = roles.get(name)
        if role and role.permissions.value != expected.value:
            live_failures.append(f"role:{name}")
    for category_name, allowed in CATEGORY_ACCESS_POLICY.items():
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            live_failures.append(f"category:{category_name}:missing")
            continue
        if category.overwrites_for(guild.default_role).view_channel is not False:
            live_failures.append(f"category:{category_name}:everyone")
        for role_name in allowed:
            role = roles.get(role_name)
            if role and category.overwrites_for(role).view_channel is not True:
                live_failures.append(f"access:{category_name}->{role_name}")
    for channel_name, policy in CHANNEL_LOCK_POLICY.items():
        channel = find_public_text_channel(guild, channel_name)
        if not channel:
            live_failures.append(f"channel:{channel_name}:missing")
            continue
        everyone = channel.overwrites_for(guild.default_role)
        if policy["mode"] in {"public_read_only", "public_read_only_bot_write"}:
            if everyone.view_channel is not True or everyone.send_messages is not False:
                live_failures.append(f"lock:{channel_name}:public")
        elif everyone.view_channel is not False:
            live_failures.append(f"lock:{channel_name}:private")
        for bot_role_name in policy.get("bot_roles", []):
            bot_role = roles.get(bot_role_name)
            if bot_role and channel.overwrites_for(bot_role).send_messages is not True:
                live_failures.append(f"bot-write:{channel_name}->{bot_role_name}")
    if live_failures:
        print("STRICT AUDIT FAIL · " + " | ".join(live_failures))
    else:
        print("STRICT AUDIT PASS · role permissions + restricted category access")
    print(f"READY · {guild.name} · {len(guild.roles)} roles · {len(guild.channels)} channels")

def build_welcome_embed(member, rules_channel=None, roles_channel=None):
    member_count = member.guild.member_count or "—"
    rules = rules_channel.mention if rules_channel else "#・𝗥𝘂𝗹𝗲𝘀"
    roles = roles_channel.mention if roles_channel else "#・𝗖𝗵𝗼𝗼𝘀𝗲・𝗥𝗼𝗹𝗲𝘀"

    embed = discord.Embed(
        title="✦ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗨𝗣𝗭𝗛𝗔 ✦",
        description=(
            f"**Welcome, {member.display_name} — you’re officially in.** {member.mention}\n\n"
            f"Member **#{member_count}**.\n\n"
            "**gaming · creators · friends**\n\n"
            "A place to play, meet people, share your work, and build a community.\n\n"
            f"Start with {rules} → choose your games in {roles}."
        ),
        color=discord.Color(0xFF4F6D),
    )
    embed.add_field(
        name="01 · 𝗦𝗧𝗔𝗥𝗧 𝗛𝗘𝗥𝗘",
        value=f"Read {rules} and get familiar with the server.",
        inline=False,
    )
    embed.add_field(
        name="02 · 𝗣𝗜𝗖𝗞 𝗬𝗢𝗨𝗥 𝗥𝗢𝗟𝗘𝗦",
        value=f"Choose your games and interests in {roles}.",
        inline=False,
    )
    embed.add_field(
        name="03 · 𝗠𝗘𝗘𝗧 𝗧𝗛𝗘 𝗖𝗢𝗠𝗠𝗨𝗡𝗜𝗧𝗬",
        value="Chat, find teammates, share projects, join events, and make friends.",
        inline=False,
    )
    embed.add_field(
        name="04 · 𝗛𝗔𝗩𝗘 𝗙𝗨𝗡",
        value="Keep it respectful, SFW, and chill. That’s it.",
        inline=False,
    )
    avatar = getattr(member, "display_avatar", None)
    avatar_url = getattr(avatar, "url", None)
    if avatar_url:
        embed.set_thumbnail(url=str(avatar_url))
    embed.set_image(url="attachment://rupzha-welcome.gif")
    embed.set_footer(text="RupZha · your space to play • create • connect")
    return embed


@bot.event
async def on_member_join(member):
    if member.guild.id != GUILD_ID:
        return
    burst = join_guard.record(member.id)
    if burst:
        security = discord.utils.get(member.guild.text_channels, name=security_log_channel_name())
        if security:
            try:
                await log_security_event(
                    security,
                    "RupZha · Join Burst Detected",
                    f"Detected {len(burst)} joins within {join_guard.window_seconds:.0f}s. No automatic punishment was applied.",
                )
            except discord.HTTPException as exc:
                print(f"WARN security log: {exc}")
    role = discord.utils.get(member.guild.roles, name="Member")
    if role and role < member.guild.me.top_role:
        try:
            await member.add_roles(role, reason="Rupzha onboarding")
        except discord.HTTPException as exc:
            print(f"WARN member role: {exc}")
    welcome = find_public_text_channel(member.guild, PUBLIC_CHANNELS["welcome"])
    rules = find_public_text_channel(member.guild, PUBLIC_CHANNELS["rules"])
    roles = find_public_text_channel(member.guild, PUBLIC_CHANNELS["roles"])
    if welcome:
        try:
            await welcome.send(
                embed=build_welcome_embed(member, rules, roles),
                file=welcome_panel_file(),
            )
        except (FileNotFoundError, discord.HTTPException) as exc:
            print(f"WARN welcome message: {exc}")

@bot.event
async def on_member_remove(member):
    if member.guild.id != GUILD_ID:
        return
    channel = find_public_text_channel(member.guild, PUBLIC_CHANNELS["welcome"])
    if channel:
        try:
            await channel.send(f"𝗚𝗢𝗢𝗗𝗕𝗬𝗘 · **{member.display_name}**")
        except discord.HTTPException:
            pass

RUPZHA_BOT_ALLOWED_ROLES = frozenset({"Founder", "Co-Founder"})


def can_use_rupzha_bot(member) -> bool:
    """Allow interactive use of RupZha only to the server's top two named ranks."""
    if member is None:
        return False
    return any(getattr(role, "name", None) in RUPZHA_BOT_ALLOWED_ROLES for role in getattr(member, "roles", []))


async def send_interaction_message(interaction: discord.Interaction, content: str, *, ephemeral: bool = True) -> bool:
    """Acknowledge an interaction exactly once, tolerating Discord's acknowledgement race."""
    try:
        if not interaction.response.is_done():
            try:
                await interaction.response.send_message(content, ephemeral=ephemeral)
                return True
            except discord.HTTPException as exc:
                if getattr(exc, "code", None) != 40060:
                    if getattr(exc, "status", None) == 404 or getattr(exc, "code", None) == 10062:
                        return False
                    raise
        try:
            await interaction.followup.send(content, ephemeral=ephemeral)
            return True
        except (discord.NotFound, discord.HTTPException) as exc:
            if getattr(exc, "status", None) == 404 or getattr(exc, "code", None) == 10062:
                return False
            raise
    except discord.NotFound:
        return False


tree = discord.app_commands.CommandTree(bot)


async def _rupzha_bot_global_check(interaction: discord.Interaction) -> bool:
    """Fail closed for every slash/context command unless the user is Founder/Co-Founder."""
    if can_use_rupzha_bot(getattr(interaction, "user", None)):
        return True
    await send_interaction_message(
        interaction,
        "RupZha bot commands are restricted to **Founder** and **Co-Founder**.",
    )
    return False


tree.interaction_check = _rupzha_bot_global_check


def ticket_rooms_category_for_guild(guild):
    return discord.utils.get(guild.categories, name=TICKET_ROOMS_CATEGORY)


async def create_ticket_channel(interaction: discord.Interaction, kind: str, *, category: str | None = None):
    guild = interaction.guild
    if guild is None or not isinstance(interaction.user, discord.Member):
        return None, "This command can only be used inside Rupzha."
    try:
        definition = ticket_type_definition(kind)
    except ValueError:
        return None, "That ticket type is not supported."
    requested_category = category or definition["category"]
    if requested_category != definition["category"]:
        return None, "That ticket type does not belong to the selected category."
    if not ticket_service.can_open(interaction.user, kind):
        return None, "Business/client tickets require the **Client** role or staff access."
    category = ticket_rooms_category_for_guild(guild)
    if category is None:
        try:
            category = await ensure_ticket_rooms_category(guild)
        except discord.HTTPException:
            return None, "The private ticket room category is unavailable; ticket creation was not attempted."
    existing = ticket_service.db.fetchone(
        "SELECT ticket_id FROM tickets WHERE guild_id = ? AND opener_id = ? AND kind = ? AND status = 'open' LIMIT 1",
        (guild.id, interaction.user.id, kind),
    )
    if existing:
        ticket = ticket_service.get_ticket(existing[0])
        channel = guild.get_channel(ticket.channel_id) if ticket else None
        return channel, "You already have an open ticket of this type."

    ticket_id = ticket_service._next_id()
    support_role = discord.utils.get(guild.roles, name="Support")
    if support_role is None:
        return None, "Support role is missing; ticket creation was not attempted."
    staff_roles = [
        role for role in guild.roles
        if role.name in {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator", "Support"}
    ]
    overwrites = build_ticket_overwrites(
        guild.default_role, interaction.user, support_role, guild.me, staff_roles=staff_roles
    )
    channel = await category.create_text_channel(
        name=f"ticket-{ticket_id.lower()}",
        overwrites=overwrites,
        reason=f"RupZha {kind} ticket opened by {interaction.user}",
    )
    try:
        ticket = ticket_service.create_ticket(
            guild.id,
            interaction.user.id,
            channel.id,
            kind,
            category=requested_category,
        )
    except sqlite3.IntegrityError:
        # Another interaction won the race. Remove this orphan channel and return
        # the already-persisted ticket instead of creating duplicate support rooms.
        try:
            await channel.delete(reason="RupZha duplicate ticket race cleanup")
        except discord.HTTPException:
            pass
        existing = ticket_service.db.fetchone(
            "SELECT ticket_id FROM tickets WHERE guild_id = ? AND opener_id = ? AND kind = ? AND status = 'open' LIMIT 1",
            (guild.id, interaction.user.id, kind),
        )
        ticket = ticket_service.get_ticket(existing[0]) if existing else None
        if ticket is None:
            return None, "Ticket creation raced and could not recover safely; please try again."
        existing_channel = guild.get_channel(ticket.channel_id)
        return existing_channel, "You already have an open ticket of this type."
    await channel.send(
        embed=discord.Embed(
            title=f"RupZha · {definition['label']}",
            description=(
                f"Ticket **{ticket.ticket_id}**\n\n"
                f"Category: **{requested_category.title()}**\n"
                f"Type: **{definition['label']}**\n\n"
                "Support will be with you shortly. Keep sensitive information inside this private channel."
            ),
            color=discord.Color(0xFF4F6D),
        ),
        view=TicketControlsView(ticket.ticket_id),
    )
    return channel, None


async def write_ticket_transcript(channel, ticket):
    TICKET_TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    path = TICKET_TRANSCRIPT_DIR / f"{ticket.ticket_id}.txt"
    lines = [
        f"RupZha Ticket Transcript — {ticket.ticket_id}",
        f"Guild: {ticket.guild_id}",
        f"Channel: {channel.id}",
        f"Opener: {ticket.opener_id}",
        f"Type: {ticket.kind}",
        f"Category: {ticket.category}",
        f"Priority: {ticket.priority}",
        f"Claimed by: {ticket.claimed_by or 'Unclaimed'}",
        f"Escalated: {ticket.escalated}",
        f"Closed reason: {ticket.closed_reason or 'Resolved'}",
        "",
    ]
    async for message in channel.history(limit=None, oldest_first=True):
        timestamp = message.created_at.isoformat()
        author = f"{message.author} ({message.author.id})"
        content = message.clean_content or ""
        if message.attachments:
            content += " " + " ".join(attachment.url for attachment in message.attachments)
        lines.append(f"[{timestamp}] {author}: {content}")
    path.write_text("\n".join(lines), encoding="utf-8")
    ticket_service.set_transcript_path(ticket.ticket_id, str(path))
    return path


async def archive_closed_ticket(guild, ticket):
    channel = guild.get_channel(ticket.channel_id)
    if channel is None:
        return False
    if ticket.status != "closed":
        return False
    try:
        if not ticket.transcript_path or not Path(ticket.transcript_path).exists():
            await write_ticket_transcript(channel, ticket)
        archive_category = await ensure_ticket_archive_category(guild)
        await channel.edit(category=archive_category, reason=f"RupZha archive {ticket.ticket_id}")
        await channel.set_permissions(guild.default_role, view_channel=False, send_messages=False, reason="RupZha archived ticket")
        opener = guild.get_member(ticket.opener_id)
        if opener:
            await channel.set_permissions(opener, view_channel=True, send_messages=False, read_message_history=True, reason="RupZha archived ticket")
        ticket_service.mark_archived(ticket.ticket_id)
        return True
    except (discord.Forbidden, discord.HTTPException, OSError) as exc:
        print(f"WARN ticket archive {ticket.ticket_id}: {exc}")
        return False


async def ticket_lifecycle_loop():
    while not bot.is_closed():
        guild = bot.get_guild(GUILD_ID)
        if guild:
            for ticket in ticket_service.due_archival_tickets():
                await archive_closed_ticket(guild, ticket)
            for ticket in ticket_service.db.fetchall(
                "SELECT ticket_id, channel_id, transcript_path FROM tickets WHERE status='archived' AND delete_at IS NOT NULL AND delete_at <= CURRENT_TIMESTAMP"
            ):
                channel = guild.get_channel(ticket["channel_id"])
                if channel is None:
                    continue
                if not ticket["transcript_path"] or not Path(ticket["transcript_path"]).exists():
                    continue
                try:
                    await channel.delete(reason=f"RupZha ticket retention expired: {ticket['ticket_id']}")
                    db.execute("DELETE FROM tickets WHERE ticket_id = ? AND status = 'archived'", (ticket["ticket_id"],))
                except (discord.Forbidden, discord.HTTPException) as exc:
                    print(f"WARN ticket deletion {ticket['ticket_id']}: {exc}")
        await asyncio.sleep(60)


TICKET_CATEGORY_LABELS = {
    "support": "🛠️ Support",
    "complaints": "🚨 Complaints & Reports",
    "business": "💼 Business / Client",
    "feedback": "⭐ Feedback",
}


class TicketTypeSelect(discord.ui.Select):
    def __init__(self, category: str):
        self.category = category
        options = [
            discord.SelectOption(label=label, value=kind, description=f"Open a private {label.lower()} ticket.")
            for kind, label in TICKET_CATEGORIES[category].items()
        ]
        super().__init__(
            placeholder="Choose what you need help with…",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"rupzha:tickets:type:{category}",
        )

    async def callback(self, interaction: discord.Interaction):
        kind = self.values[0]
        label = TICKET_CATEGORIES[self.category][kind]
        await interaction.response.defer(ephemeral=True)
        try:
            channel, error = await create_ticket_channel(interaction, kind, category=self.category)
        except discord.Forbidden:
            await interaction.followup.send("I can't create the private ticket channel with my current permissions.", ephemeral=True)
            return
        if error:
            await interaction.followup.send(f"{error} {channel.mention if channel else ''}".strip(), ephemeral=True)
            return
        await interaction.followup.send(f"**{label}** ticket created: {channel.mention}", ephemeral=True)


class TicketTypeView(discord.ui.View):
    def __init__(self, category: str):
        super().__init__(timeout=900)
        self.category = category
        self.add_item(TicketTypeSelect(category))
        back = discord.ui.Button(label="← Back to categories", style=discord.ButtonStyle.secondary, custom_id=f"rupzha:tickets:back:{category}")
        back.callback = self.go_back
        self.add_item(back)

    async def go_back(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=build_ticket_panel_embed(), view=TicketPanelView())


def build_ticket_panel_embed():
    return discord.Embed(
        title="🎫・𝗧𝗜𝗖𝗞𝗘𝗧 𝗦𝗨𝗣𝗣𝗢𝗥𝗧",
        description=(
            "Need help? Choose a category below and then pick the exact reason.\n\n"
            "Your ticket opens as a **private room** for you and the RupZha support team.\n\n"
            "🛠️ **Support** — questions, bugs, bots, accounts, channels\n"
            "🚨 **Complaints & Reports** — members, moderation, security, complaints\n"
            "💼 **Business / Client** — services, projects, billing, partnerships\n"
            "⭐ **Feedback** — ratings, suggestions, praise, improvements"
        ),
        color=discord.Color(0xFF4F6D),
    )


class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def choose(self, interaction: discord.Interaction, category: str):
        label = TICKET_CATEGORY_LABELS[category]
        embed = discord.Embed(
            title=f"🎫 {label}",
            description="Choose the option that best matches your issue. If you're unsure, use **General Support**.",
            color=discord.Color(0xFF4F6D),
        )
        # The public panel is shared by the whole server. Never edit it for one user's
        # selection; doing so makes every member see that user's category screen.
        await interaction.response.send_message(embed=embed, view=TicketTypeView(category), ephemeral=True)

    @discord.ui.button(label="Support", emoji="🛠️", style=discord.ButtonStyle.primary, custom_id="rupzha:tickets:category:support")
    async def support(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.choose(interaction, "support")

    @discord.ui.button(label="Complaints & Reports", emoji="🚨", style=discord.ButtonStyle.danger, custom_id="rupzha:tickets:category:complaints")
    async def complaints(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.choose(interaction, "complaints")

    @discord.ui.button(label="Business / Client", emoji="💼", style=discord.ButtonStyle.success, custom_id="rupzha:tickets:category:business")
    async def business(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.choose(interaction, "business")

    @discord.ui.button(label="Feedback", emoji="⭐", style=discord.ButtonStyle.secondary, custom_id="rupzha:tickets:category:feedback")
    async def feedback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.choose(interaction, "feedback")


class TicketCloseModal(discord.ui.Modal, title="Close RupZha Ticket"):
    reason = discord.ui.TextInput(
        label="Closure reason",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500,
        placeholder="Briefly explain how this ticket was resolved…",
    )

    async def on_submit(self, interaction: discord.Interaction):
        current = ticket_service.get_by_channel(interaction.channel.id if interaction.channel else 0)
        if current is None:
            await interaction.response.send_message("This is not a RupZha ticket channel.", ephemeral=True)
            return
        if interaction.user.id != current.opener_id and not _staff_check(interaction):
            await interaction.response.send_message("Only the ticket opener or staff can close this ticket.", ephemeral=True)
            return
        if current.status != "open":
            await interaction.response.send_message("This ticket is already closed.", ephemeral=True)
            return
        updated = ticket_service.close_ticket(current.ticket_id, str(self.reason.value))
        try:
            await write_ticket_transcript(interaction.channel, updated)
            await interaction.channel.set_permissions(interaction.guild.default_role, view_channel=False, send_messages=False, reason="RupZha ticket closed")
            opener = interaction.guild.get_member(updated.opener_id)
            if opener:
                await interaction.channel.set_permissions(opener, view_channel=True, send_messages=False, read_message_history=True, reason="RupZha ticket feedback access")
        except (discord.Forbidden, discord.HTTPException, OSError) as exc:
            await interaction.response.send_message(f"Ticket state was saved, but the Discord close operation failed: {exc}", ephemeral=True)
            return
        await interaction.response.send_message(f"Ticket **{updated.ticket_id}** closed. It will be archived now and deleted after 24 hours.")
        await interaction.channel.send(
            embed=discord.Embed(
                title="⭐ Ticket Feedback",
                description="Thanks for using RupZha support. Rate your experience from **1–5 stars**. You can also leave an optional comment.",
                color=discord.Color(0xF5B642),
            ),
            view=TicketFeedbackView(updated.ticket_id, updated.opener_id),
        )
        await archive_closed_ticket(interaction.guild, updated)


class TicketControlsView(discord.ui.View):
    def __init__(self, ticket_id: str):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
        self._add_button("Claim", "🙋", discord.ButtonStyle.primary, "claim")
        self._add_button("Unclaim", "↩️", discord.ButtonStyle.secondary, "unclaim")
        self._add_button("Priority", "🚦", discord.ButtonStyle.secondary, "priority")
        self._add_button("Escalate", "🚨", discord.ButtonStyle.danger, "escalate")
        self._add_button("Close", "🔒", discord.ButtonStyle.danger, "close")

    def _add_button(self, label, emoji, style, action):
        button = discord.ui.Button(label=label, emoji=emoji, style=style, custom_id=f"rupzha:tickets:{action}:{self.ticket_id}")
        button.callback = self._action_callback(action)
        self.add_item(button)

    def _action_callback(self, action):
        async def callback(interaction):
            current = ticket_service.get_ticket(self.ticket_id)
            if current is None or interaction.channel is None or current.channel_id != interaction.channel.id:
                await send_interaction_message(interaction, "This ticket is no longer available.")
                return
            if action in {"claim", "unclaim", "priority", "escalate"} and not _staff_check(interaction):
                await send_interaction_message(interaction, "Staff only.")
                return
            if action == "claim":
                if current.status != "open":
                    await send_interaction_message(interaction, "Only open tickets can be claimed.")
                    return
                if current.claimed_by and current.claimed_by != interaction.user.id:
                    await send_interaction_message(interaction, "This ticket is already claimed by another staff member.")
                    return
                ticket_service.claim_ticket(current.ticket_id, interaction.user.id)
                await send_interaction_message(interaction, f"Ticket **{current.ticket_id}** claimed by {interaction.user.mention}.")
            elif action == "unclaim":
                if current.claimed_by != interaction.user.id:
                    await send_interaction_message(interaction, "Only the staff member who claimed this ticket can unclaim it.")
                    return
                ticket_service.unclaim_ticket(current.ticket_id)
                await send_interaction_message(interaction, f"Ticket **{current.ticket_id}** is unclaimed.")
            elif action == "priority":
                order = ["low", "normal", "high", "urgent"]
                next_priority = order[(order.index(current.priority) + 1) % len(order)]
                updated = ticket_service.set_priority(current.ticket_id, next_priority)
                await send_interaction_message(interaction, f"Priority changed to **{updated.priority.upper()}**.")
            elif action == "escalate":
                updated = ticket_service.set_escalated(current.ticket_id, not current.escalated)
                await send_interaction_message(interaction, f"Escalation **{'enabled' if updated.escalated else 'cleared'}** for {updated.ticket_id}.")
            elif action == "close":
                if interaction.user.id != current.opener_id and not _staff_check(interaction):
                    await send_interaction_message(interaction, "Only the ticket opener or staff can close this ticket.")
                    return
                await interaction.response.send_modal(TicketCloseModal())
        return callback


class TicketFeedbackModal(discord.ui.Modal, title="RupZha Ticket Feedback"):
    comment = discord.ui.TextInput(
        label="What could we improve? (optional)",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=2000,
        placeholder="Tell us what went well or what we should improve…",
    )

    def __init__(self, ticket_id: str, rating: int, opener_id: int):
        super().__init__(timeout=300)
        self.ticket_id = ticket_id
        self.rating = rating
        self.opener_id = opener_id

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user.id != self.opener_id:
            await interaction.response.send_message("Only the ticket opener can submit this feedback.", ephemeral=True)
            return
        try:
            feedback = ticket_service.add_feedback(
                self.ticket_id,
                interaction.user.id,
                self.rating,
                str(self.comment.value or ""),
            )
        except ValueError as exc:
            await interaction.response.send_message(str(exc), ephemeral=True)
            return
        await interaction.response.send_message(
            f"Thanks — your **{feedback['rating']}/5** rating was recorded privately."
            + (" Your written feedback was saved too." if feedback["comment"] else ""),
            ephemeral=True,
        )


class TicketFeedbackView(discord.ui.View):
    def __init__(self, ticket_id: str, opener_id: int):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
        self.opener_id = opener_id
        for rating, style in (
            (1, discord.ButtonStyle.secondary),
            (2, discord.ButtonStyle.secondary),
            (3, discord.ButtonStyle.secondary),
            (4, discord.ButtonStyle.primary),
            (5, discord.ButtonStyle.success),
        ):
            button = discord.ui.Button(
                label=str(rating),
                emoji="⭐",
                style=style,
                custom_id=f"rupzha:tickets:rating:{ticket_id}:{rating}",
            )
            button.callback = self._rating_callback(rating)
            self.add_item(button)

    def _rating_callback(self, rating: int):
        async def callback(interaction: discord.Interaction):
            await self.rate(interaction, rating)
        return callback

    async def rate(self, interaction: discord.Interaction, rating: int):
        if interaction.user.id != self.opener_id:
            await interaction.response.send_message("Only the ticket opener can rate this ticket.", ephemeral=True)
            return
        ticket = ticket_service.get_ticket(self.ticket_id)
        if ticket is None or ticket.status not in {"closed", "archived"}:
            await interaction.response.send_message("This ticket is no longer available for feedback.", ephemeral=True)
            return
        existing = ticket_service.db.fetchone("SELECT feedback_id FROM ticket_feedback WHERE ticket_id = ?", (self.ticket_id,))
        if existing:
            await interaction.response.send_message("Feedback has already been submitted for this ticket.", ephemeral=True)
            return
        await interaction.response.send_modal(TicketFeedbackModal(self.ticket_id, rating, self.opener_id))

@tree.command(name="ticket", description="Open a private Rupzha support, report, or client ticket.")
@discord.app_commands.describe(kind="Ticket type.")
@discord.app_commands.choices(kind=[
    discord.app_commands.Choice(name="Support", value="support"),
    discord.app_commands.Choice(name="Report", value="report"),
    discord.app_commands.Choice(name="Client", value="client"),
])
async def ticket(interaction: discord.Interaction, kind: discord.app_commands.Choice[str]):
    await interaction.response.defer(ephemeral=True)
    try:
        channel, error = await create_ticket_channel(interaction, kind.value)
    except discord.Forbidden:
        await interaction.followup.send("I can't create the private ticket channel with my current permissions.", ephemeral=True)
        return
    if error:
        if channel:
            await interaction.followup.send(f"{error} {channel.mention}", ephemeral=True)
        else:
            await interaction.followup.send(error, ephemeral=True)
        return
    await interaction.followup.send(f"Ticket created: {channel.mention}", ephemeral=True)


@tree.command(name="ticket-close", description="Close the current Rupzha ticket.")
async def ticket_close(interaction: discord.Interaction):
    if interaction.guild is None or interaction.channel is None:
        await interaction.response.send_message("This command must be used inside a ticket.", ephemeral=True)
        return
    current = ticket_service.get_by_channel(interaction.channel.id)
    if current is None:
        await interaction.response.send_message("This is not a Rupzha ticket channel.", ephemeral=True)
        return
    if interaction.user.id != current.opener_id and not _staff_check(interaction):
        await interaction.response.send_message("Only the ticket opener or staff can close this ticket.", ephemeral=True)
        return
    ticket_service.close_ticket(current.ticket_id)
    opener = interaction.guild.get_member(current.opener_id)
    await interaction.channel.set_permissions(interaction.guild.default_role, view_channel=False, send_messages=False, reason="RupZha ticket closed")
    if opener:
        await interaction.channel.set_permissions(opener, view_channel=True, send_messages=False, read_message_history=True, reason="RupZha ticket feedback access")
    await interaction.response.send_message(f"Ticket **{current.ticket_id}** closed.")
    await interaction.channel.send(
        embed=discord.Embed(
            title="⭐ Ticket Feedback",
            description="Thanks for using RupZha support. If you opened this ticket, please rate your experience from **1–5 stars**. You can also leave an optional comment after choosing a rating.",
            color=discord.Color(0xF5B642),
        ),
        view=TicketFeedbackView(current.ticket_id, current.opener_id),
    )


@tree.command(name="ticket-reopen", description="Reopen the current Rupzha ticket for staff.")
@discord.app_commands.default_permissions(manage_channels=True)
async def ticket_reopen(interaction: discord.Interaction):
    if not _staff_check(interaction) or interaction.channel is None:
        await interaction.response.send_message("Staff only, inside a ticket channel.", ephemeral=True)
        return
    current = ticket_service.get_by_channel(interaction.channel.id)
    if current is None:
        await interaction.response.send_message("This is not a Rupzha ticket channel.", ephemeral=True)
        return
    reopened = ticket_service.reopen_ticket(current.ticket_id)
    opener = interaction.guild.get_member(reopened.opener_id)
    active_category = ticket_rooms_category_for_guild(interaction.guild) or await ensure_ticket_rooms_category(interaction.guild)
    await interaction.channel.edit(category=active_category, reason="RupZha ticket reopened")
    if opener:
        await interaction.channel.set_permissions(opener, view_channel=True, send_messages=True, read_message_history=True)
    bot.add_view(TicketControlsView(reopened.ticket_id))
    await interaction.response.send_message(f"Ticket **{reopened.ticket_id}** reopened.")


bot.add_view(TicketPanelView())


@tree.command(name="profile", description="Show your Rupzha XP and level profile.")
async def profile(interaction: discord.Interaction):
    data = community_service.get_profile(interaction.user.id)
    await interaction.response.send_message(
        embed=discord.Embed(
            title=f"RupZha · {interaction.user.display_name}",
            description=f"**Level {data['level']}**\n**{data['xp']} XP**",
        ),
        ephemeral=True,
    )


@tree.command(name="suggest", description="Submit a community suggestion.")
@discord.app_commands.describe(content="Your suggestion.")
async def suggest(interaction: discord.Interaction, content: str):
    suggestion_id = community_service.create_suggestion(interaction.user.id, content)
    await interaction.response.send_message(f"Suggestion **#{suggestion_id}** submitted. Thanks for the idea.", ephemeral=True)


@tree.command(name="poll", description="Create a simple community poll.")
@discord.app_commands.describe(question="Poll question.", option1="First option.", option2="Second option.", option3="Optional third option.")
async def poll(interaction: discord.Interaction, question: str, option1: str, option2: str, option3: str = ""):
    options = [option1, option2] + ([option3] if option3.strip() else [])
    embed = discord.Embed(title="RupZha · Community Poll", description=question)
    embed.add_field(name="Options", value="\n".join(f"{i}️⃣ {option}" for i, option in enumerate(options, 1)), inline=False)
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    for emoji in ("1️⃣", "2️⃣", "3️⃣")[:len(options)]:
        await message.add_reaction(emoji)


@tree.command(name="event", description="Create a community event announcement.")
@discord.app_commands.describe(title="Event title.", starts_at="Start time in ISO format, e.g. 2026-11-01T20:00:00+05:30.")
async def event(interaction: discord.Interaction, title: str, starts_at: str):
    if not _staff_check(interaction):
        await interaction.response.send_message("Staff only.", ephemeral=True)
        return
    event_id = community_service.create_event(interaction.user.id, title, starts_at)
    channel = discord.utils.find(lambda c: c.name in {"・𝗘𝘃𝗲𝗻𝘁𝘀", "・Events"}, interaction.guild.text_channels)
    target = channel or interaction.channel
    await target.send(embed=discord.Embed(title=f"RupZha · {title}", description=f"Event **#{event_id}**\nStarts: **{starts_at}**"))
    await interaction.response.send_message(f"Event **#{event_id}** created.", ephemeral=True)


@tree.command(name="remind", description="Create a reminder that will be delivered by DM.")
@discord.app_commands.describe(minutes="Minutes from now.", message="Reminder text.")
async def remind(interaction: discord.Interaction, minutes: discord.app_commands.Range[int, 1, 10080], message: str):
    from datetime import datetime, timezone

    remind_at = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    reminder_id = community_service.create_reminder(interaction.user.id, message, remind_at.isoformat())
    await interaction.response.send_message(f"Reminder **#{reminder_id}** set for **{minutes} minutes** from now.", ephemeral=True)


@tree.command(name="lfg", description="Find teammates for a game.")
@discord.app_commands.describe(game="Game name.", details="What you are looking for.")
async def lfg(interaction: discord.Interaction, game: str, details: str):
    await interaction.response.send_message(
        embed=discord.Embed(title=f"RupZha · LFG · {game}", description=f"{interaction.user.mention} is looking for teammates.\n\n{details}")
    )


@bot.event
async def on_message(message: discord.Message):
    if message.guild is None or message.guild.id != GUILD_ID:
        return
    # Discord's Administrator permission bypasses channel overwrites. Enforce
    # the dedicated-channel rule again at the message boundary.
    if message.author.bot and not third_party_bot_message_allowed(message.author.id, message.channel.id):
        try:
            await message.delete(reason="Third-party bot restricted to its dedicated channel")
            print(f"BOT MESSAGE BLOCKED · {message.author} · #{message.channel.name}")
        except discord.HTTPException as exc:
            print(f"WARN BOT MESSAGE BLOCK FAILED · {message.author} · #{message.channel.name}: {exc}")
        return
    if message.author.bot:
        return
    if legacy_bot_prefix_is_blocked(message.content, getattr(message.channel, "name", "")):
        try:
            await message.delete(reason="Legacy bot command outside the designated bot command channel")
        except discord.HTTPException:
            pass
        return
    before = community_service.get_profile(message.author.id)
    gained = community_service.record_message(message.author.id)
    if gained:
        after = community_service.get_profile(message.author.id)
        if after["level"] > before["level"]:
            try:
                await message.channel.send(f"🎉 {message.author.mention} reached **Level {after['level']}**!")
            except discord.HTTPException:
                pass


async def reminder_loop():
    from datetime import datetime, timezone

    while not bot.is_closed():
        now = datetime.now(timezone.utc).isoformat()
        due = db.fetchall("SELECT reminder_id, member_id, message FROM reminders WHERE sent = 0 AND remind_at <= ?", (now,))
        for row in due:
            user = bot.get_user(row["member_id"]) or await bot.fetch_user(row["member_id"])
            try:
                await user.send(f"RupZha reminder: {row['message']}")
                db.execute("UPDATE reminders SET sent = 1 WHERE reminder_id = ?", (row["reminder_id"],))
            except (discord.HTTPException, discord.NotFound):
                db.execute("UPDATE reminders SET sent = 1 WHERE reminder_id = ?", (row["reminder_id"],))
        await asyncio.sleep(30)


@tree.command(name="project-status", description="View or update a Rupzha project status.")
@discord.app_commands.describe(project_id="Project identifier.", status="New status (staff only).", summary="Client-safe status summary (staff only).")
async def project_status(interaction: discord.Interaction, project_id: str, status: str = "", summary: str = ""):
    role_names = {role.name for role in getattr(interaction.user, "roles", ())}
    if status or summary:
        if not can_use_staff_command(interaction, {"Founder", "Co-Founder", "Administrator", "Operations", "Manager"}):
            await interaction.response.send_message("Only Rupzha staff can update project status.", ephemeral=True)
            return
        set_project_status(db, project_id, status, summary)
        await interaction.response.send_message(f"Project **{project_id}** updated.", ephemeral=True)
        return
    if not can_view_project(role_names):
        await interaction.response.send_message("You don't have access to this project.", ephemeral=True)
        return
    embed = build_client_status_embed(db, project_id, role_names)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="internal-note", description="Record a private internal operations note.")
@discord.app_commands.describe(note="Private note; never posted publicly.")
@discord.app_commands.default_permissions(manage_guild=True)
async def internal_note(interaction: discord.Interaction, note: str):
    role_names = {role.name for role in getattr(interaction.user, "roles", ())}
    if not can_use_staff_command(interaction, {"Founder", "Co-Founder", "Administrator", "Operations"}):
        await interaction.response.send_message("Operations staff only.", ephemeral=True)
        return
    case_id = create_internal_case(db, interaction.user.id, role_names, note)
    if case_id is None:
        await interaction.response.send_message("Operations staff only.", ephemeral=True)
        return
    await interaction.response.send_message(f"Internal case **#{case_id}** recorded privately.", ephemeral=True)


@tree.command(name="ping", description="Check Rupzha bot latency.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong · {round(bot.latency * 1000)}ms", ephemeral=True)

@tree.command(name="clear", description="Delete recent messages in this channel.")
@discord.app_commands.describe(amount="Number of messages to delete (1-100).")
@discord.app_commands.default_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: discord.app_commands.Range[int, 1, 100]):
    if not can_use_staff_command(
        interaction,
        {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator"},
        require="manage_messages",
    ):
        await interaction.response.send_message("Moderation staff only: Manage Messages or a configured staff role is required.", ephemeral=True)
        return
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("This command only works in text channels.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    try:
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted **{len(deleted)}** messages.", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to delete messages here.", ephemeral=True)


def should_delete_server_message(message) -> bool:
    """Return True only for unpinned messages during the explicit server purge."""
    return not bool(getattr(message, "pinned", False))


async def delete_server_message(message) -> None:
    """Delete a server-clean target using the PartialMessage-compatible API."""
    await message.delete()


@tree.command(name="server-clean", description="Delete all unpinned messages across Rupzha.")
@discord.app_commands.describe(confirm="Set to True to permanently delete unpinned messages.")
@discord.app_commands.default_permissions(manage_messages=True)
async def server_clean(interaction: discord.Interaction, confirm: bool = False):
    """Explicitly purge server message history while preserving every pinned message."""
    # Acknowledge immediately: a busy gateway or command-sync delay must never
    # turn a valid moderation command into Discord's 10062 Unknown interaction.
    await interaction.response.defer(ephemeral=True, thinking=True)
    if interaction.guild is None or not can_use_staff_command(
        interaction,
        {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator"},
        require="manage_messages",
    ):
        await interaction.followup.send("Moderation staff only: Manage Messages or a configured staff role is required.", ephemeral=True)
        return
    if not confirm:
        await interaction.followup.send(
            "This permanently deletes unpinned messages across the server. "
            "Pinned messages are preserved. Run `/server-clean confirm:True` to start.",
            ephemeral=True,
        )
        return

    deleted = 0
    preserved = 0
    failed = 0
    scanned_channels = 0
    seen_channel_ids = set()
    channels = list(interaction.guild.text_channels) + list(getattr(interaction.guild, "threads", []))

    for channel in channels:
        if channel.id in seen_channel_ids:
            continue
        seen_channel_ids.add(channel.id)
        scanned_channels += 1
        try:
            async for message in channel.history(limit=None, oldest_first=False):
                if not should_delete_server_message(message):
                    preserved += 1
                    continue
                try:
                    await delete_server_message(message)
                    deleted += 1
                except discord.NotFound:
                    pass
                except discord.Forbidden:
                    failed += 1
                except discord.HTTPException as exc:
                    if exc.status == 429:
                        await asyncio.sleep(getattr(exc, "retry_after", 2.0))
                        try:
                            await delete_server_message(message)
                            deleted += 1
                        except discord.HTTPException:
                            failed += 1
                    else:
                        failed += 1
        except (discord.Forbidden, discord.HTTPException) as exc:
            failed += 1
            print(f"WARN server clean #{getattr(channel, 'name', channel.id)}: {exc}")

    await interaction.followup.send(
        f"Server clean finished.\n"
        f"• Channels scanned: **{scanned_channels}**\n"
        f"• Messages deleted: **{deleted}**\n"
        f"• Pinned messages preserved: **{preserved}**\n"
        f"• Messages/channels that could not be deleted: **{failed}**",
        ephemeral=True,
    )
    print(
        f"SERVER CLEAN · by={interaction.user.id} channels={scanned_channels} "
        f"deleted={deleted} preserved={preserved} failed={failed}"
    )


def can_use_staff_command(interaction: discord.Interaction, allowed: set[str], *, require: str | None = None) -> bool:
    """Authorize staff commands by role, server ownership, or explicit Discord permission.

    Named roles remain the normal policy. The guild owner and Discord Administrator
    are always trusted. A command may additionally require a concrete permission
    (for example Manage Messages for message deletion), preventing a stale role-name
    list from locking out a legitimate owner/admin while still failing closed for members.
    """
    member = getattr(interaction, "user", None)
    guild = getattr(interaction, "guild", None)
    if member is None or guild is None or not hasattr(member, "id"):
        return False
    if getattr(guild, "owner_id", None) == member.id:
        return True
    permissions = getattr(member, "guild_permissions", None)
    if permissions is not None and getattr(permissions, "administrator", False):
        return True
    if is_staff(member, allowed):
        return True
    if require is not None and permissions is not None and getattr(permissions, require, False):
        return True
    return False


def _staff_check(interaction: discord.Interaction) -> bool:
    return can_use_staff_command(interaction, set(STAFF_ROLES))


def _role_check(interaction: discord.Interaction, allowed: set[str]) -> bool:
    return can_use_staff_command(interaction, allowed)


def _can_act(interaction: discord.Interaction, target: discord.Member, action: str) -> bool:
    return can_execute_moderation(interaction.user, target, action)


async def _record_moderation(interaction: discord.Interaction, target: discord.Member, action: str, reason: str):
    record_case(db, interaction.guild.id, target.id, interaction.user.id, action, reason)


@tree.command(name="warn", description="Warn a member and record a moderation case.")
@discord.app_commands.describe(member="Member to warn.", reason="Reason for the warning.")
@discord.app_commands.default_permissions(manage_messages=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "Rupzha moderation"):
    if not _can_act(interaction, member, "warn"):
        await interaction.response.send_message("You are not allowed to warn that member.", ephemeral=True)
        return
    await _record_moderation(interaction, member, "warn", reason)
    await interaction.response.send_message(f"Warned **{member}**. Case recorded.", ephemeral=True)


@tree.command(name="warnings", description="View recent warnings and moderation cases for a member.")
@discord.app_commands.describe(member="Member to inspect.")
@discord.app_commands.default_permissions(manage_messages=True)
async def warnings(interaction: discord.Interaction, member: discord.Member):
    if not can_use_staff_command(interaction, {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator"}):
        await interaction.response.send_message("Moderation staff only.", ephemeral=True)
        return
    cases = get_recent_cases(db, interaction.guild.id, member.id)
    if not cases:
        await interaction.response.send_message(f"No moderation cases for **{member}**.", ephemeral=True)
        return
    lines = [f"`#{row['case_id']}` · **{row['action']}** · {row['reason']}" for row in cases]
    await interaction.response.send_message("\n".join(lines), ephemeral=True)


@tree.command(name="kick", description="Kick a member from Rupzha.")
@discord.app_commands.describe(member="Member to kick.", reason="Optional reason.")
@discord.app_commands.default_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Rupzha moderation"):
    if not _can_act(interaction, member, "kick"):
        await interaction.response.send_message("You can't kick that member.", ephemeral=True)
        return
    try:
        await member.kick(reason=f"{interaction.user}: {reason}")
        await _record_moderation(interaction, member, "kick", reason)
        await interaction.response.send_message(f"Kicked **{member}**.")
    except discord.Forbidden:
        await interaction.response.send_message("I can't kick that member because of role hierarchy/permissions.", ephemeral=True)


@tree.command(name="ban", description="Ban a member from Rupzha.")
@discord.app_commands.describe(member="Member to ban.", reason="Optional reason.")
@discord.app_commands.default_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Rupzha moderation"):
    if not _can_act(interaction, member, "ban"):
        await interaction.response.send_message("You can't ban that member.", ephemeral=True)
        return
    try:
        await member.ban(reason=f"{interaction.user}: {reason}")
        await _record_moderation(interaction, member, "ban", reason)
        await interaction.response.send_message(f"Banned **{member}**.")
    except discord.Forbidden:
        await interaction.response.send_message("I can't ban that member because of role hierarchy/permissions.", ephemeral=True)


@tree.command(name="timeout", description="Timeout a member for up to 28 days.")
@discord.app_commands.describe(member="Member to timeout.", minutes="Duration in minutes.", reason="Optional reason.")
@discord.app_commands.default_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: discord.app_commands.Range[int, 1, 40320], reason: str = "Rupzha moderation"):
    if not _can_act(interaction, member, "timeout"):
        await interaction.response.send_message("You can't timeout that member.", ephemeral=True)
        return
    try:
        await member.timeout(discord.utils.utcnow() + timedelta(minutes=minutes), reason=f"{interaction.user}: {reason}")
        await _record_moderation(interaction, member, "timeout", reason)
        await interaction.response.send_message(f"Timed out **{member}** for **{minutes} minutes**.")
    except discord.Forbidden:
        await interaction.response.send_message("I can't timeout that member because of role hierarchy/permissions.", ephemeral=True)


@tree.command(name="slowmode", description="Set slowmode for the current text channel.")
@discord.app_commands.describe(seconds="Slowmode delay from 0 to 21600 seconds.")
@discord.app_commands.default_permissions(manage_channels=True)
async def slowmode(interaction: discord.Interaction, seconds: discord.app_commands.Range[int, 0, 21600]):
    if not can_use_staff_command(interaction, {"Founder", "Co-Founder", "Administrator", "Operations"}, require="manage_channels") or not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("Management staff only, and this must be a text channel.", ephemeral=True)
        return
    await interaction.channel.edit(slowmode_delay=seconds, reason=f"Rupzha slowmode by {interaction.user}")
    await interaction.response.send_message(f"Slowmode set to **{seconds}s**.")


async def _set_channel_lock(interaction: discord.Interaction, locked: bool):
    if not can_use_staff_command(interaction, {"Founder", "Co-Founder", "Administrator", "Operations"}, require="manage_channels") or not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("Management staff only, and this must be a text channel.", ephemeral=True)
        return
    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = not locked
    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite, reason=f"Rupzha {'lock' if locked else 'unlock'} by {interaction.user}")
    await interaction.response.send_message(f"Channel **{'locked' if locked else 'unlocked'}**.")


@tree.command(name="lock", description="Lock the current text channel for @everyone.")
@discord.app_commands.default_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    await _set_channel_lock(interaction, True)


@tree.command(name="unlock", description="Unlock the current text channel for @everyone.")
@discord.app_commands.default_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    await _set_channel_lock(interaction, False)

@tree.command(name="announce", description="Post an official announcement in the announcements channel.")
@discord.app_commands.describe(message="Announcement text.")
@discord.app_commands.default_permissions(manage_guild=True)
async def announce(interaction: discord.Interaction, message: str):
    if not _role_check(interaction, {"Founder", "Co-Founder", "Administrator", "Operations"}):
        await interaction.response.send_message("Operations staff only.", ephemeral=True)
        return
    channel = discord.utils.get(interaction.guild.text_channels, name=PUBLIC_CHANNELS["announcements"]) if interaction.guild else None
    if not channel:
        await interaction.response.send_message("Announcements channel not found.", ephemeral=True)
        return
    embed = discord.Embed(title="𝗥𝗨𝗣𝗭𝗛𝗔 𝗔𝗡𝗡𝗢𝗨𝗡𝗖𝗘𝗠𝗘𝗡𝗧", description=message)
    embed.set_footer(text=f"Posted by {interaction.user.display_name}")
    await channel.send(embed=embed)
    await interaction.response.send_message("Announcement posted.", ephemeral=True)

async def cleanup_dedicated_bot_messages(guild):
    """Remove recent dedicated-bot messages that slipped into other channels."""
    bot_ids = {408785106942164992: 1564050781307670629}
    deleted = 0
    for channel in guild.text_channels:
        for bot_id, allowed_channel_id in bot_ids.items():
            if channel.id == allowed_channel_id:
                continue
            try:
                async for message in channel.history(limit=100):
                    if message.author.id == bot_id:
                        await message.delete()
                        deleted += 1
                        print(f"OWO CHAT CLEANED · #{channel.name} · message={message.id}")
            except (discord.Forbidden, discord.HTTPException) as exc:
                print(f"WARN OWO CHAT CLEANUP · #{channel.name}: {exc}")
    print(f"OWO CHAT AUDIT · deleted={deleted}")
    return deleted


@bot.event
async def on_ready():
    global reminder_task, ticket_lifecycle_task
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found")
        return
    print(f"Logged in as {bot.user}")
    # Repair the visible welcome board immediately, but never let a Discord API
    # stall prevent the bot from starting its core services.
    welcome_channel = find_public_text_channel(guild, PUBLIC_CHANNELS["welcome"])
    if welcome_channel:
        print(f"WELCOME REPAIR START · #{welcome_channel.name}")
        try:
            panel = await asyncio.wait_for(ensure_welcome_panel(welcome_channel), timeout=15)
        except asyncio.TimeoutError:
            print("WARN welcome repair timed out; continuing startup")
            panel = None
        if panel:
            print(f"WELCOME BOARD REPAIRED · #{welcome_channel.name} · {panel.id}")
    else:
        print("WARN welcome channel not found during startup")
    # Channel names are reconciled by setup_server using canonical policies.
    # Do not rename the whole guild on every startup: that caused API churn and
    # made permission/audit checks race against channel renames.
    if reminder_task is None or reminder_task.done():
        reminder_task = asyncio.create_task(reminder_loop())
    if ticket_lifecycle_task is None or ticket_lifecycle_task.done():
        ticket_lifecycle_task = asyncio.create_task(ticket_lifecycle_loop())
    print("CORE RECONCILE START")
    try:
        await asyncio.wait_for(setup_server(guild), timeout=120)
    except asyncio.TimeoutError:
        print("WARN core reconcile timed out after 120s; continuing with live services")
    print("CORE RECONCILE END")
    # Sync guild commands before the slower historical cleanup so newly added
    # moderation commands become visible immediately after startup.
    try:
        tree.copy_global_to(guild=guild)
        synced = await asyncio.wait_for(tree.sync(guild=guild), timeout=20)
        print(f"SLASH COMMANDS EARLY SYNCED · {len(synced)}")
    except (asyncio.TimeoutError, discord.HTTPException) as exc:
        print(f"WARN early slash sync: {exc}")
    try:
        await asyncio.wait_for(cleanup_dedicated_bot_messages(guild), timeout=45)
    except asyncio.TimeoutError:
        print("WARN OWO CHAT CLEANUP timed out; continuing")
    try:
        ticket_panel = await asyncio.wait_for(ensure_ticket_panel(guild), timeout=15)
    except asyncio.TimeoutError:
        print("WARN ticket panel repair timed out")
        ticket_panel = None
    if ticket_panel:
        print(f"TICKET SYSTEM READY · panel={ticket_panel.id} · private_category={TICKET_ROOMS_CATEGORY}")
    report = await verify_live_guild(guild)
    if report["status"] == "PASS":
        print("STRICT AUDIT PASS · full upgrade contract")
    else:
        print("STRICT AUDIT FAIL · " + " | ".join(report["failures"]))
    for line in readiness_lines():
        print(line)
    try:
        tree.copy_global_to(guild=guild)
        synced = await tree.sync(guild=guild)
        print(f"SLASH COMMANDS SYNCED · {len(synced)}")
    except discord.HTTPException as exc:
        print(f"WARN slash sync: {exc}")
    print("RUPZHA BOT ONLINE")

if __name__ == "__main__":
    _INSTANCE_LOCK = INSTANCE_LOCK_PATH.open("w")
    try:
        fcntl.flock(_INSTANCE_LOCK.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("RupZha instance already running; refusing duplicate gateway process.")
        sys.exit(0)
    bot.run(TOKEN)
