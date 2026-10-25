import os
import asyncio
from datetime import timedelta
from pathlib import Path
import discord
from dotenv import load_dotenv

from storage import Database
from moderation import JoinGuard, can_moderate, get_recent_cases, is_staff, log_security_event, record_case, security_log_channel_name

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1554830636454514708
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
db = Database(DB_PATH)
db.initialize()
join_guard = JoinGuard(window_seconds=10.0, threshold=8)

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
ROLE_PERMISSION_POLICY = {
    "Founder": discord.Permissions(administrator=True),
    "Co-Founder": discord.Permissions(administrator=True),
    "Administrator": discord.Permissions(administrator=True),
    "Operations": discord.Permissions(manage_guild=True, manage_channels=True, manage_messages=True, view_audit_log=True, kick_members=True, ban_members=True),
    "Manager": discord.Permissions(manage_messages=True, manage_threads=True, view_audit_log=True),
    "Moderator": discord.Permissions(manage_messages=True, manage_threads=True, moderate_members=True, kick_members=True),
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

CATEGORY_ACCESS_POLICY = {
    "╭・𝗖𝗟𝗜𝗘𝗡𝗧 𝗛𝗨𝗕": {"Client", "Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Support"},
    "╭・𝗧𝗘𝗔𝗠 𝗛𝗤": {"Developer", "Designer", "Content Creator", "Founder", "Co-Founder", "Administrator", "Operations", "Manager"},
    "╭・𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦": {"Founder", "Co-Founder", "Administrator", "Operations"},
    "╭・𝗔𝗣𝗣𝗦 & 𝗧𝗢𝗢𝗟𝗦": {"Founder", "Co-Founder", "Administrator", "Operations"},
    "╭・𝗪𝗜𝗖𝗞": {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator"},
    "╭・𝗧𝗜𝗖𝗞𝗘𝗧・𝗧𝗢𝗢𝗟": {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Support"},
    "╭・𝗦𝗧𝗔𝗧𝗕𝗢𝗧": {"Founder", "Co-Founder", "Administrator", "Operations", "Manager"},
    "╭・𝗔𝗥𝗖𝗔𝗡𝗘": {"Founder", "Co-Founder", "Administrator", "Operations", "Manager"},
    "╭・𝗫𝗘𝗡𝗢𝗡": {"Founder", "Co-Founder", "Administrator"},
    "╭・𝗖𝗔𝗥𝗟・𝗕𝗢𝗧": {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator"},
}

# Child-channel locks tighten category permissions without changing the category model.
# Modes: public_read_only, public_read_only_bot_write, client_read_only,
# restricted_read_only, restricted_bot_write.
CHANNEL_LOCK_POLICY = {
    "・𝗪𝗲𝗹𝗰𝗼𝗺𝗲": {"mode": "public_read_only"},
    "・𝗥𝘂𝗹𝗲𝘀": {"mode": "public_read_only"},
    "・𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁𝘀": {"mode": "public_read_only"},
    "・𝗖𝗵𝗼𝗼𝘀𝗲・𝗥𝗼𝗹𝗲𝘀": {"mode": "public_read_only"},
    "・𝗛𝗼𝘄・𝗜𝘁・𝗪𝗼𝗿𝗸𝘀": {"mode": "public_read_only"},
    "・𝗙𝗔𝗤": {"mode": "public_read_only"},
    "・𝗣𝗿𝗼𝗷𝗲𝗰𝘁・𝗦𝘁𝗮𝘁𝘂𝘀": {"mode": "client_read_only"},
    "・𝗟𝗼𝗴𝘀": {"mode": "restricted_read_only"},
    "・𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆・𝗟𝗼𝗴𝘀": {"mode": "restricted_bot_write", "bot_roles": ["Wick"]},
    "・𝗔𝗻𝘁𝗶𝗥𝗮𝗶𝗱・𝗟𝗼𝗴𝘀": {"mode": "restricted_bot_write", "bot_roles": ["Wick"]},
    "・𝗧𝗶𝗰𝗸𝗲𝘁・𝗣𝗮𝗻𝗲𝗹": {"mode": "public_read_only_bot_write", "bot_roles": ["Ticket Tool"]},
    "・𝗦𝘁𝗮𝘁𝘀・𝗗𝗮𝘀𝗵𝗯𝗼𝗮𝗿𝗱": {"mode": "restricted_bot_write", "bot_roles": ["Statbot"]},
    "・𝗔𝗰𝘁𝗶𝘃𝗶𝘁𝘆・𝗦𝘁𝗮𝘁𝘀": {"mode": "restricted_bot_write", "bot_roles": ["Statbot"]},
    "・𝗟𝗲𝘃𝗲𝗹・𝗨𝗽𝘀": {"mode": "public_read_only_bot_write", "bot_roles": ["Arcane"]},
    "・𝗕𝗮𝗰𝗸𝘂𝗽𝘀": {"mode": "restricted_bot_write", "bot_roles": ["Xenon"]},
    "・𝗖𝗮𝗿𝗹・𝗟𝗼𝗴𝘀": {"mode": "restricted_bot_write", "bot_roles": ["carl-bot"]},
}

READ_ONLY_STAFF_ROLES = {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator", "Support"}

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
    "Voice Chat", "Announcements", "Event Alerts", "Giveaways", "Community Updates",
]
ONBOARDING_STEPS = ["profile", "purpose", "interests", "games", "notifications", "finish"]
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


PUBLIC_CHANNELS = {
    "welcome": "・𝗪𝗲𝗹𝗰𝗼𝗺𝗲",
    "rules": "・𝗥𝘂𝗹𝗲𝘀",
    "announcements": "・𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁𝘀",
    "roles": "・𝗖𝗵𝗼𝗼𝘀𝗲・𝗥𝗼𝗹𝗲𝘀",
    "how": "・𝗛𝗼𝘄・𝗜𝘁・𝗪𝗼𝗿𝗸𝘀",
    "faq": "・𝗙𝗔𝗤",
}

WELCOME = """# 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗨𝗣𝗭𝗛𝗔

**Gaming • Community • Building**

A clean space to play, meet people, share work, and build something useful.

**𝗦𝗧𝗔𝗥𝗧 𝗛𝗘𝗥𝗘**
> Read **𝗥𝘂𝗹𝗲𝘀**
> Choose your games in **𝗖𝗵𝗼𝗼𝘀𝗲・𝗥𝗼𝗹𝗲𝘀**
> Check **𝗛𝗼𝘄・𝗜𝘁・𝗪𝗼𝗿𝗸𝘀**
> Then jump into the community.

Keep it clean. Keep it respectful. Have fun.
"""

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

async def seed(channel, content):
    try:
        async for message in channel.history(limit=20):
            if message.author == bot.user:
                return
        await channel.send(content)
    except (discord.Forbidden, discord.HTTPException) as exc:
        print(f"WARN seed #{channel.name}: {exc}")

async def setup_server(guild):
    roles = {r.name: r for r in guild.roles}
    me = guild.me
    if not me:
        print("WARN: bot member unavailable")
        return

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

    # The bot only manages roles below its own role. Role ordering is intentionally not
    # mutated automatically here; Discord's role UI is safer for the final staff hierarchy.
    # All functional roles remain below the bot role.

    # Strict role permissions: only the explicitly privileged staff roles get power.
    for name, perms in ROLE_PERMISSION_POLICY.items():
        role = roles.get(name)
        if role and role < me.top_role:
            try:
                await role.edit(permissions=perms, colour=ROLE_COLOURS.get(name, role.colour), reason="Rupzha role permissions")
            except discord.HTTPException as exc:
                print(f"WARN role {name}: {exc}")

    # Game hubs stay hidden until a member selects the matching game role.
    for game in GAME_ROLES:
        role = roles.get(game)
        if not role:
            continue
        category = discord.utils.get(guild.categories, name=f"╭・𝗚𝗔𝗠𝗘・{game.upper()}")
        if not category:
            category = discord.utils.find(lambda c: game.lower() in c.name.lower() and "𝗚𝗔𝗠𝗘" in c.name, guild.categories)
        if category:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True),
            }
            # Only management/moderation staff need every game hub; Support and business roles stay out.
            for staff_name in ("Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator"):
                staff = roles.get(staff_name)
                if staff:
                    overwrites[staff] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True)
            try:
                await category.edit(overwrites=overwrites, reason="Rupzha game hub permissions")
            except discord.HTTPException as exc:
                print(f"WARN game hub {game}: {exc}")

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
            await category.edit(overwrites=overwrites, reason="Rupzha strict role access")
        except discord.HTTPException as exc:
            print(f"WARN restricted category {category_name}: {exc}")

    # Child-channel locks make public documentation read-only and sensitive bot logs write-only for their integration bot.
    for channel in guild.text_channels:
        policy = CHANNEL_LOCK_POLICY.get(channel.name)
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

    start = discord.utils.get(guild.categories, name="╭・𝗦𝗧𝗔𝗥𝗧 𝗛𝗘𝗥𝗘")
    if not start:
        print("WARN: START HERE category missing")
        return

    channels = {c.name: c for c in start.text_channels}
    content = {
        PUBLIC_CHANNELS["welcome"]: WELCOME,
        PUBLIC_CHANNELS["rules"]: RULES,
        PUBLIC_CHANNELS["how"]: HOW,
        PUBLIC_CHANNELS["faq"]: FAQ,
        PUBLIC_CHANNELS["announcements"]: "# 𝗥𝗨𝗣𝗭𝗛𝗔 𝗔𝗡𝗡𝗢𝗨𝗡𝗖𝗘𝗠𝗘𝗡𝗧𝗦\n\nOfficial server news, events, updates, and important notices will appear here.",
    }
    for name, text in content.items():
        if name in channels:
            await seed(channels[name], text)

    # Native Discord Community Onboarding is the only onboarding entry point.
    # Do not seed a post-join bot onboarding panel; it would duplicate/conflict with the pre-join flow.

    # Live audit: report only mismatches so permission regressions are visible in logs.
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
        channel = discord.utils.get(guild.text_channels, name=channel_name)
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
        title="𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗨𝗣𝗭𝗛𝗔",
        description=(
            f"{member.mention} **you’re officially in.**\n\n"
            f"Welcome, **{member.display_name}**. You’re member **#{member_count}** of the community.\n\n"
            f"Gaming • Community • Building\n\n"
            f"Start with {rules} → choose games in {roles}."
        ),
    )
    embed.add_field(name="01 · 𝗥𝗘𝗔𝗗", value=f"Start with {rules}", inline=False)
    embed.add_field(name="02 · 𝗖𝗛𝗢𝗢𝗦𝗘", value=f"Pick your games in {roles}", inline=False)
    embed.add_field(name="03 · 𝗝𝗢𝗜𝗡 𝗜𝗡", value="Jump into the community, find teammates, and have fun.", inline=False)
    embed.set_footer(text="RupZha • Gaming • Community • Building")
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
    welcome = discord.utils.get(member.guild.text_channels, name=PUBLIC_CHANNELS["welcome"])
    rules = discord.utils.get(member.guild.text_channels, name=PUBLIC_CHANNELS["rules"])
    roles = discord.utils.get(member.guild.text_channels, name=PUBLIC_CHANNELS["roles"])
    if welcome:
        try:
            await welcome.send(embed=build_welcome_embed(member, rules, roles))
        except discord.HTTPException as exc:
            print(f"WARN welcome message: {exc}")

@bot.event
async def on_member_remove(member):
    if member.guild.id != GUILD_ID:
        return
    channel = discord.utils.get(member.guild.text_channels, name=PUBLIC_CHANNELS["welcome"])
    if channel:
        try:
            await channel.send(f"𝗚𝗢𝗢𝗗𝗕𝗬𝗘 · **{member.display_name}**")
        except discord.HTTPException:
            pass

tree = discord.app_commands.CommandTree(bot)

@tree.command(name="ping", description="Check Rupzha bot latency.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong · {round(bot.latency * 1000)}ms", ephemeral=True)

@tree.command(name="clear", description="Delete recent messages in this channel.")
@discord.app_commands.describe(amount="Number of messages to delete (1-100).")
@discord.app_commands.default_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: discord.app_commands.Range[int, 1, 100]):
    if not _staff_check(interaction):
        await interaction.response.send_message("Staff only.", ephemeral=True)
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

def _staff_check(interaction: discord.Interaction) -> bool:
    return isinstance(interaction.user, discord.Member) and is_staff(interaction.user, set(STAFF_ROLES))


def _can_act(interaction: discord.Interaction, target: discord.Member) -> bool:
    return _staff_check(interaction) and can_moderate(interaction.user, target)


async def _record_moderation(interaction: discord.Interaction, target: discord.Member, action: str, reason: str):
    record_case(db, interaction.guild.id, target.id, interaction.user.id, action, reason)


@tree.command(name="warn", description="Warn a member and record a moderation case.")
@discord.app_commands.describe(member="Member to warn.", reason="Reason for the warning.")
@discord.app_commands.default_permissions(moderate_members=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "Rupzha moderation"):
    if not _can_act(interaction, member):
        await interaction.response.send_message("You are not allowed to warn that member.", ephemeral=True)
        return
    await _record_moderation(interaction, member, "warn", reason)
    await interaction.response.send_message(f"Warned **{member}**. Case recorded.", ephemeral=True)


@tree.command(name="warnings", description="View recent warnings and moderation cases for a member.")
@discord.app_commands.describe(member="Member to inspect.")
@discord.app_commands.default_permissions(moderate_members=True)
async def warnings(interaction: discord.Interaction, member: discord.Member):
    if not _staff_check(interaction):
        await interaction.response.send_message("Staff only.", ephemeral=True)
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
    if not _can_act(interaction, member):
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
    if not _can_act(interaction, member):
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
    if not _can_act(interaction, member):
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
    if not _staff_check(interaction) or not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("Staff only, and this must be a text channel.", ephemeral=True)
        return
    await interaction.channel.edit(slowmode_delay=seconds, reason=f"Rupzha slowmode by {interaction.user}")
    await interaction.response.send_message(f"Slowmode set to **{seconds}s**.")


async def _set_channel_lock(interaction: discord.Interaction, locked: bool):
    if not _staff_check(interaction) or not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("Staff only, and this must be a text channel.", ephemeral=True)
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
    if not _staff_check(interaction):
        await interaction.response.send_message("Staff only.", ephemeral=True)
        return
    channel = discord.utils.get(interaction.guild.text_channels, name=PUBLIC_CHANNELS["announcements"]) if interaction.guild else None
    if not channel:
        await interaction.response.send_message("Announcements channel not found.", ephemeral=True)
        return
    embed = discord.Embed(title="𝗥𝗨𝗣𝗭𝗛𝗔 𝗔𝗡𝗡𝗢𝗨𝗡𝗖𝗘𝗠𝗘𝗡𝗧", description=message)
    embed.set_footer(text=f"Posted by {interaction.user.display_name}")
    await channel.send(embed=embed)
    await interaction.response.send_message("Announcement posted.", ephemeral=True)

@bot.event
async def on_ready():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found")
        return
    print(f"Logged in as {bot.user}")
    await setup_server(guild)
    try:
        tree.copy_global_to(guild=guild)
        synced = await tree.sync(guild=guild)
        print(f"SLASH COMMANDS SYNCED · {len(synced)}")
    except discord.HTTPException as exc:
        print(f"WARN slash sync: {exc}")
    print("RUPZHA BOT ONLINE")

if __name__ == "__main__":
    bot.run(TOKEN)
