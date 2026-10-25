import asyncio
from types import SimpleNamespace

import bot
from verify_full_upgrade import build_report, readiness_lines, read_onboarding_enabled


def test_verification_report_marks_missing_guild_state():
    report = build_report(None)
    assert report["status"] == "FAIL"
    assert "guild" in report["failures"]


def test_readiness_lines_are_stable():
    lines = readiness_lines()
    assert lines == ["STORAGE READY", "MODERATION READY", "TICKETS READY", "COMMUNITY READY", "OPERATIONS READY"]


def test_onboarding_reader_handles_discord_async_accessor():
    async def onboarding():
        return SimpleNamespace(enabled=True)

    guild = SimpleNamespace(onboarding=onboarding)
    assert asyncio.run(read_onboarding_enabled(guild)) is True


def test_protected_categories_and_channels_are_in_policy():
    required_categories = {
        "╭・𝗖𝗟𝗜𝗘𝗡𝗧 𝗛𝗨𝗕",
        "╭・𝗧𝗘𝗔𝗠 𝗛𝗤",
        "╭・𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦",
        "╭・𝗔𝗣𝗣𝗦 & 𝗧𝗢𝗢𝗟𝗦",
        "╭・𝗧𝗜𝗖𝗞𝗘𝗧・𝗧𝗢𝗢𝗟",
    }
    assert required_categories <= set(bot.CATEGORY_ACCESS_POLICY)
    assert "・𝗥𝘂𝗹𝗲𝘀" in bot.CHANNEL_LOCK_POLICY
    assert "・𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆・𝗟𝗼𝗴𝘀" in bot.CHANNEL_LOCK_POLICY


def test_required_commands_are_registered():
    names = {command.name for command in bot.tree.get_commands()}
    required = {
        "warn", "warnings", "kick", "ban", "timeout", "slowmode", "lock", "unlock",
        "ticket", "ticket-close", "ticket-reopen", "profile", "suggest", "poll", "event",
        "remind", "lfg", "project-status", "internal-note",
    }
    assert required <= names


def test_native_onboarding_is_not_replaced_by_bot_onboarding_wall():
    source = open("bot.py", encoding="utf-8").read()
    assert "Native Discord Community Onboarding is the only onboarding entry point." in source
    assert "class OnboardingEntryView" in source
    assert "@bot.event\nasync def on_member_join" in source


def test_game_hub_policy_requires_matching_role_and_hides_other_game_roles():
    from types import SimpleNamespace
    from verify_full_upgrade import check_game_hub_policy

    class Overwrite:
        def __init__(self, view): self.view_channel = view

    class Category:
        def __init__(self): self.overrides = {}
        def overwrites_for(self, role): return self.overrides.get(role, Overwrite(None))

    everyone = object(); valorant = object(); minecraft = object()
    category = Category()
    category.overrides[everyone] = Overwrite(False)
    category.overrides[valorant] = Overwrite(True)
    category.overrides[minecraft] = Overwrite(False)
    roles = {"Valorant": valorant, "Minecraft": minecraft}
    categories = {"╭・𝗚𝗔𝗠𝗘・VALORANT": category}
    failures = check_game_hub_policy(everyone, roles, categories, ["Valorant", "Minecraft"])
    assert failures == []


def test_optional_roles_are_purposeful_and_permissionless():
    assert set(bot.OPTIONAL_ROLE_POLICY) == {"Trial Moderator", "Event Host", "QA / Tester", "Partner", "Community Helper"}
    for name, spec in bot.OPTIONAL_ROLE_POLICY.items():
        assert spec["permissions"] == 0
        assert spec["auto_assign"] is False
        assert bot.ROLE_COLOURS[name].value != 0


def test_unknown_custom_role_with_native_power_is_flagged():
    from verify_full_upgrade import dangerous_permission_names
    import discord
    role = SimpleNamespace(name="OMEN", managed=False, permissions=discord.Permissions(administrator=True))
    assert "administrator" in dangerous_permission_names(role)


def test_managed_integration_roles_are_never_reconciled():
    from verify_full_upgrade import should_reconcile_role
    managed = SimpleNamespace(name="Arcane", managed=True)
    assert should_reconcile_role(managed) is False


def test_role_colors_cover_game_and_optional_roles():
    assert all(bot.ROLE_COLOURS[name].value != 0 for name in bot.GAME_ROLES)
    assert all(bot.ROLE_COLOURS[name].value != 0 for name in bot.OPTIONAL_ROLE_POLICY)


def test_onboarding_managed_roles_are_permissionless_policy_roles():
    assert set(bot.ONBOARDING_MANAGED_ROLES) <= set(bot.ROLE_PERMISSION_POLICY)
    for name in bot.ONBOARDING_MANAGED_ROLES:
        assert bot.ROLE_PERMISSION_POLICY[name].value == 0


def test_third_party_bot_channels_are_isolated():
    assert bot.THIRD_PARTY_BOT_CHANNELS == {
        "OwO": "🤖・・𝗢𝘄𝗢",
        "Pokétwo": "🎮・・𝗣𝗼𝗸𝗲𝘁𝘄𝗼",
        "Koya": "🌸・・𝗞𝗼𝘆𝗮",
    }
    assert bot.THIRD_PARTY_BOT_CHANNEL_POLICIES["OwO"]["bot_role"] == "OwO"
    assert bot.THIRD_PARTY_BOT_CHANNEL_POLICIES["Pokétwo"]["bot_role"] == "Pokétwo"
    assert bot.THIRD_PARTY_BOT_CHANNEL_POLICIES["Koya"]["bot_role"] == "Koya"


def test_third_party_bot_channel_access_reads_public_but_cannot_write_elsewhere():
    policy = bot.build_third_party_bot_overwrite("OwO", "🤖・・𝗢𝘄𝗢", "📢・・𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁𝘀")
    assert policy["allowed"] is False
    assert policy["view_channel"] is True
    assert policy["read_message_history"] is True
    assert policy["send_messages"] is False
    assert policy["send_messages_in_threads"] is False
    assert policy["create_public_threads"] is False
    assert policy["create_private_threads"] is False
    assert policy["use_application_commands"] is False
    assert policy["add_reactions"] is False


def test_third_party_bot_own_channel_is_fully_operational():
    own = bot.build_third_party_bot_overwrite("OwO", "🤖・・𝗢𝘄𝗢", "🤖・・𝗢𝘄𝗢")
    assert own["allowed"] is True
    assert own["view_channel"] is True
    assert own["read_message_history"] is True
    assert own["send_messages"] is True
    assert own["send_messages_in_threads"] is True
    assert own["use_application_commands"] is True
    assert own["add_reactions"] is True


def test_third_party_bot_private_channels_are_hidden():
    policy = bot.build_third_party_bot_overwrite(
        "OwO", "🤖・・𝗢𝘄𝗢", "📋・・𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆・𝗟𝗼𝗴𝘀", is_private=True
    )
    assert policy["view_channel"] is False
    assert policy["read_message_history"] is False
    assert policy["send_messages"] is False
    assert policy["use_application_commands"] is False


def test_every_non_special_bot_gets_a_private_command_scope_policy():
    special = set(bot.SPECIAL_BOT_CHANNEL_POLICIES)
    assert {"Wick", "Ticket Tool", "Statbot", "Arcane", "Xenon", "carl-bot"} <= special
    policy = bot.build_universal_bot_overwrite("Mimu", "🤖・・𝗠𝗶𝗺𝘂", "📢・・𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁𝘀")
    assert policy["view_channel"] is True
    assert policy["read_message_history"] is True
    assert policy["send_messages"] is False
    assert policy["use_application_commands"] is False


def test_every_bot_own_channel_is_fully_operational():
    own = bot.build_universal_bot_overwrite("Mimu", "🤖・・𝗠𝗶𝗺𝘂", "🤖・・𝗠𝗶𝗺𝘂")
    assert all(own[k] is True for k in ("view_channel", "read_message_history", "send_messages", "send_messages_in_threads", "use_application_commands", "add_reactions"))


def test_special_bot_keeps_only_its_functional_channels_writable():
    assert bot.SPECIAL_BOT_CHANNEL_POLICIES["Wick"] == {"📋・・𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆・𝗟𝗼𝗴𝘀", "📋・・𝗔𝗻𝘁𝗶𝗥𝗮𝗶𝗱・𝗟𝗼𝗴𝘀"}
    assert bot.SPECIAL_BOT_CHANNEL_POLICIES["Ticket Tool"] == {"🎫・・𝗧𝗶𝗰𝗸𝗲𝘁・𝗣𝗮𝗻𝗲𝗹"}
