from __future__ import annotations

import unicodedata

REQUIRED_CATEGORIES = {
    "╭・𝗖𝗟𝗜𝗘𝗡𝗧 𝗛𝗨𝗕",
    "╭・𝗧𝗘𝗔𝗠 𝗛𝗤",
    "╭・𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦",
    "╭・𝗔𝗣𝗣𝗦 & 𝗧𝗢𝗢𝗟𝗦",
    "╭・𝗕𝗢𝗧・𝗟𝗢𝗚𝗦",
    "╭・𝗧𝗜𝗖𝗞𝗘𝗧・𝗥𝗢𝗢𝗠𝗦",
}
REQUIRED_CHANNELS = {
    "・𝗪𝗲𝗹𝗰𝗼𝗺𝗲", "・𝗥𝘂𝗹𝗲𝘀", "・𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁𝘀",
    "・𝗛𝗼𝘄・𝗜𝘁・𝗪𝗼𝗿𝗸𝘀", "・𝗙𝗔𝗤", "・𝗧𝗶𝗰𝗸𝗲𝘁・𝗣𝗮𝗻𝗲𝗹",
}


def readiness_lines() -> list[str]:
    return ["STORAGE READY", "MODERATION READY", "TICKETS READY", "COMMUNITY READY", "OPERATIONS READY"]


async def read_onboarding_enabled(guild) -> bool:
    accessor = getattr(guild, "onboarding", None)
    if callable(accessor):
        onboarding = await accessor()
    else:
        onboarding = accessor
    return bool(getattr(onboarding, "enabled", False))


def _normalized_label(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = value.replace("・", " ").replace("／", "/")
    return " ".join(value.split())


def _channel_tail(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    if "・・" in value:
        value = value.split("・・", 1)[1]
    return value.lstrip("・").strip()


def check_game_hub_policy(everyone_role, roles, categories, game_roles):
    failures = []
    category_index = {_normalized_label(name): category for name, category in categories.items()}
    for game in game_roles:
        expected_name = _normalized_label(f"╭・𝗚𝗔𝗠𝗘・{game.upper()}")
        category = category_index.get(expected_name)
        if category is None:
            failures.append(f"game:{game}:category-missing")
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


def managed_utility_bot_security_failures(roles, bot_names) -> list[str]:
    failures = []
    for name in bot_names:
        role = roles.get(name)
        if not role or not role.managed:
            continue
        dangerous = [name for name in dangerous_permission_names(role) if name != "manage_messages"]
        if dangerous:
            failures.append(f"bot-role:{name}:managed-dangerous={','.join(dangerous)}")
    return failures


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

    failures.extend(managed_utility_bot_security_failures(roles, bot.BOT_COMMAND_CHANNELS_BY_BOT))

    for category_name in REQUIRED_CATEGORIES:
        category = categories.get(category_name)
        if category is None:
            failures.append(f"category:{category_name}:missing")
            continue
        if category.overwrites_for(guild.default_role).view_channel is not False:
            failures.append(f"category:{category_name}:everyone")

    for channel_name in REQUIRED_CHANNELS:
        if not any(_channel_tail(actual_name) == _channel_tail(channel_name) for actual_name in channels):
            failures.append(f"channel:{channel_name}:missing")

    # The utility-bot area has one shared room for general utilities plus
    # dedicated public rooms for OwO, Pokétwo, and Koya.
    bot_category = categories.get("╭・𝗕𝗢𝗧・𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦")
    if bot_category is None:
        failures.append("category:bot-commands:missing")
    else:
        command_children = [c for c in bot_category.channels if getattr(c, "type", None).name == "text"]
        failures.extend(bot.check_bot_command_layout(command_children))

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
