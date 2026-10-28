import os
import asyncio
from datetime import timedelta
import discord
from dotenv import load_dotenv

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

ROLE_ORDER = [
    "Founder", "Co-Founder", "Administrator", "Operations", "Manager",
    "Moderator", "Support", "Developer", "Designer", "Content Creator",
    "Client", "Verified", "Member", "Valorant", "Minecraft", "GTA V",
    "CS2", "Fortnite", "Roblox", "Among Us", "Apex Legends",
    "BGMI / PUBG", "Other Games",
]

GAME_ROLES = ROLE_ORDER[13:]
STAFF_ROLES = ROLE_ORDER[:7]

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

class GameSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, value=name, description=GAME_DESCRIPTIONS[name])
            for name in GAME_ROLES
        ]
        super().__init__(
            custom_id="rupzha:game_roles",
            placeholder="𝗖𝗵𝗼𝗼𝘀𝗲 𝘆𝗼𝘂𝗿 𝗴𝗮𝗺𝗲𝘀...",
            min_values=0,
            max_values=len(options),
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        if not isinstance(member, discord.Member):
            await interaction.response.send_message("This selector only works inside Rupzha.", ephemeral=True)
            return

        selected = set(self.values)
        role_map = {r.name: r for r in member.guild.roles if r.name in GAME_ROLES}
        remove = [r for name, r in role_map.items() if name not in selected and r in member.roles]
        add = [role_map[name] for name in selected if name in role_map and role_map[name] not in member.roles]

        try:
            if remove:
                await member.remove_roles(*remove, reason="Rupzha game role update")
            if add:
                await member.add_roles(*add, reason="Rupzha game role update")
            if selected:
                chosen = ", ".join(sorted(selected))
                msg = f"𝗚𝗔𝗠𝗘 𝗥𝗢𝗟𝗘𝗦 𝗨𝗣𝗗𝗔𝗧𝗘𝗗\n\n{chosen}\n\nYour selected game hubs are now unlocked."
            else:
                msg = "𝗚𝗔𝗠𝗘 𝗥𝗢𝗟𝗘𝗦 𝗖𝗟𝗘𝗔𝗥𝗘𝗗\n\nAll game hubs have been removed."
            await interaction.response.send_message(msg, ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("I can't manage one of those roles. Please contact staff.", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("Discord rejected the update temporarily. Try again.", ephemeral=True)

class RolePanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GameSelect())

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

    # The bot only manages roles below its own role. Role ordering is intentionally not
    # mutated automatically here; Discord's role UI is safer for the final staff hierarchy.
    # All functional roles remain below the bot role.

    # Conservative permissions: staff roles manage the workspace; public roles remain non-privileged.
    permissions = {
        "Founder": discord.Permissions(administrator=True),
        "Co-Founder": discord.Permissions(administrator=True),
        "Administrator": discord.Permissions(administrator=True),
        "Operations": discord.Permissions(manage_guild=True, manage_channels=True, manage_messages=True, view_audit_log=True, kick_members=True, ban_members=True),
        "Manager": discord.Permissions(manage_messages=True, manage_threads=True, view_audit_log=True),
        "Moderator": discord.Permissions(manage_messages=True, manage_threads=True, moderate_members=True, kick_members=True),
        "Support": discord.Permissions(manage_threads=True),
    }
    for name, perms in permissions.items():
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
            for staff_name in STAFF_ROLES:
                staff = roles.get(staff_name)
                if staff:
                    overwrites[staff] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True)
            try:
                await category.edit(overwrites=overwrites, reason="Rupzha game hub permissions")
            except discord.HTTPException as exc:
                print(f"WARN game hub {game}: {exc}")

    # Business workspace: client-facing area is available to Clients + staff; team/ops stay internal.
    private_access = {
        "╭・𝗖𝗟𝗜𝗘𝗡𝗧 𝗛𝗨𝗕": ["Client"] + STAFF_ROLES,
        "╭・𝗧𝗘𝗔𝗠 𝗛𝗤": ["Developer", "Designer", "Content Creator"] + STAFF_ROLES,
        "╭・𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦": STAFF_ROLES,
        "╭・𝗔𝗣𝗣𝗦 & 𝗧𝗢𝗢𝗟𝗦": STAFF_ROLES,
    }
    for category_name, allowed in private_access.items():
        category = discord.utils.get(guild.categories, name=category_name)
        if not category:
            continue
        overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        for role_name in allowed:
            role = roles.get(role_name)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True)
        try:
            await category.edit(overwrites=overwrites, reason="Rupzha private workspace permissions")
        except discord.HTTPException as exc:
            print(f"WARN private category {category_name}: {exc}")

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

    roles_channel = channels.get(PUBLIC_CHANNELS["roles"])
    if roles_channel:
        try:
            found = False
            async for message in roles_channel.history(limit=20):
                if message.author == bot.user and message.components:
                    found = True
                    break
            if not found:
                embed = discord.Embed(
                    title="𝗖𝗛𝗢𝗢𝗦𝗘 𝗬𝗢𝗨𝗥 𝗚𝗔𝗠𝗘𝗦",
                    description="Select every game you play. You can change your choices anytime.\n\nYour selections unlock the matching game hubs.",
                )
                await roles_channel.send(embed=embed, view=RolePanel())
        except (discord.Forbidden, discord.HTTPException) as exc:
            print(f"WARN role panel: {exc}")

    print(f"READY · {guild.name} · {len(guild.roles)} roles · {len(guild.channels)} channels")

@bot.event
async def on_member_join(member):
    if member.guild.id != GUILD_ID:
        return
    role = discord.utils.get(member.guild.roles, name="Member")
    if role and role < member.guild.me.top_role:
        try:
            await member.add_roles(role, reason="Rupzha onboarding")
        except discord.HTTPException as exc:
            print(f"WARN member role: {exc}")
    welcome = discord.utils.get(member.guild.text_channels, name=PUBLIC_CHANNELS["welcome"])
    roles = discord.utils.get(member.guild.text_channels, name=PUBLIC_CHANNELS["roles"])
    if welcome:
        try:
            await welcome.send(f"𝗪𝗘𝗟𝗖𝗢𝗠𝗘 {member.mention} · Start in {roles.mention if roles else '𝗖𝗵𝗼𝗼𝘀𝗲・𝗥𝗼𝗹𝗲𝘀'}.")
        except discord.HTTPException:
            pass

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
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message("This command only works in text channels.", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    try:
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted **{len(deleted)}** messages.", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("I don't have permission to delete messages here.", ephemeral=True)

@tree.command(name="kick", description="Kick a member from Rupzha.")
@discord.app_commands.describe(member="Member to kick.", reason="Optional reason.")
@discord.app_commands.default_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Rupzha moderation"):
    if member == interaction.user or member.top_role >= interaction.user.top_role:
        await interaction.response.send_message("You can't kick that member.", ephemeral=True)
        return
    try:
        await member.kick(reason=f"{interaction.user}: {reason}")
        await interaction.response.send_message(f"Kicked **{member}**.")
    except discord.Forbidden:
        await interaction.response.send_message("I can't kick that member because of role hierarchy/permissions.", ephemeral=True)

@tree.command(name="timeout", description="Timeout a member for up to 28 days.")
@discord.app_commands.describe(member="Member to timeout.", minutes="Duration in minutes.", reason="Optional reason.")
@discord.app_commands.default_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: discord.app_commands.Range[int, 1, 40320], reason: str = "Rupzha moderation"):
    if member == interaction.user or member.top_role >= interaction.user.top_role:
        await interaction.response.send_message("You can't timeout that member.", ephemeral=True)
        return
    try:
        await member.timeout(discord.utils.utcnow() + timedelta(minutes=minutes), reason=f"{interaction.user}: {reason}")
        await interaction.response.send_message(f"Timed out **{member}** for **{minutes} minutes**.")
    except discord.Forbidden:
        await interaction.response.send_message("I can't timeout that member because of role hierarchy/permissions.", ephemeral=True)

@tree.command(name="announce", description="Post an official announcement in the announcements channel.")
@discord.app_commands.describe(message="Announcement text.")
@discord.app_commands.default_permissions(manage_guild=True)
async def announce(interaction: discord.Interaction, message: str):
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
    bot.add_view(RolePanel())
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

bot.run(TOKEN)
