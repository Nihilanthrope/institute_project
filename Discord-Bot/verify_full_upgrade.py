from __future__ import annotations

REQUIRED_CATEGORIES = {
    "╭・𝗖𝗟𝗜𝗘𝗡𝗧 𝗛𝗨𝗕",
    "╭・𝗧𝗘𝗔𝗠 𝗛𝗤",
    "╭・𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦",
    "╭・𝗔𝗣𝗣𝗦 & 𝗧𝗢𝗢𝗟𝗦",
    "╭・𝗧𝗜𝗖𝗞𝗘𝗧・𝗧𝗢𝗢𝗟",
}
REQUIRED_CHANNELS = {"・𝗪𝗲𝗹𝗰𝗼𝗺𝗲", "・𝗥𝘂𝗹𝗲𝘀", "・𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁𝘀", "・𝗖𝗵𝗼𝗼𝘀𝗲・𝗥𝗼𝗹𝗲𝘀"}


def readiness_lines() -> list[str]:
    return ["STORAGE READY", "MODERATION READY", "TICKETS READY", "COMMUNITY READY", "OPERATIONS READY"]


async def read_onboarding_enabled(guild) -> bool:
    accessor = getattr(guild, "onboarding", None)
    if callable(accessor):
        onboarding = await accessor()
    else:
        onboarding = accessor
    return bool(getattr(onboarding, "enabled", False))


def check_game_hub_policy(everyone_role, roles, categories, game_roles):
    failures = []
    for game in game_roles:
        category = categories.get(f"╭・𝗚𝗔𝗠𝗘・{game.upper()}")
        if category is None:
            continue
        if category.overwrites_for(everyone_role).view_channel is not False:
            failures.append(f"game:{game}:everyone")
        game_role = roles.get(game)
        if game_role and category.overwrites_for(game_role).view_channel is not True:
            failures.append(f"game:{game}:role")
        for other in game_roles:
            if other == game:
                continue
            other_role = roles.get(other)
            if other_role and category.overwrites_for(other_role).view_channel is not False:
                failures.append(f"game:{game}:leak:{other}")
    return failures

def dangerous_permission_names(role) -> list[str]:
    attrs = ("administrator", "manage_guild", "manage_roles", "manage_channels", "manage_webhooks", "kick_members", "ban_members", "moderate_members", "mention_everyone", "manage_messages")
    return [name for name in attrs if getattr(role.permissions, name, False)]


def should_reconcile_role(role) -> bool:
    return not getattr(role, "managed", False)


def build_report(guild, *, onboarding_enabled: bool | None = None) -> dict:
    import bot

    failures: list[str] = []
    if guild is None:
        return {"status": "FAIL", "failures": ["guild"]}

    roles = {role.name: role for role in guild.roles}
    channels = {channel.name: channel for channel in guild.text_channels}
    categories = {category.name: category for category in guild.categories}

    for role in guild.roles:
        if role.is_default() or role.managed or role.name in bot.ROLE_PERMISSION_POLICY:
            continue
        if dangerous_permission_names(role):
            failures.append(f"role:unexpected-power:{role.name}")

    for role_name, expected in bot.ROLE_PERMISSION_POLICY.items():
        role = roles.get(role_name)
        if role and role.permissions.value != expected.value:
            failures.append(f"role:{role_name}")

    for category_name in REQUIRED_CATEGORIES:
        category = categories.get(category_name)
        if category is None:
            failures.append(f"category:{category_name}:missing")
            continue
        if category.overwrites_for(guild.default_role).view_channel is not False:
            failures.append(f"category:{category_name}:everyone")

    for channel_name in REQUIRED_CHANNELS:
        if channel_name not in channels:
            failures.append(f"channel:{channel_name}:missing")

    if onboarding_enabled is False:
        failures.append("onboarding:disabled")

    failures.extend(check_game_hub_policy(guild.default_role, roles, categories, bot.GAME_ROLES))

    command_names = {command.name for command in bot.tree.get_commands()}
    required_commands = {"warn", "ban", "timeout", "ticket", "profile", "project-status"}
    missing_commands = required_commands - command_names
    failures.extend(f"command:{name}:missing" for name in sorted(missing_commands))

    return {"status": "PASS" if not failures else "FAIL", "failures": failures}


async def verify_live_guild(guild) -> dict:
    onboarding_enabled = await read_onboarding_enabled(guild) if guild is not None else False
    return build_report(guild, onboarding_enabled=onboarding_enabled)
