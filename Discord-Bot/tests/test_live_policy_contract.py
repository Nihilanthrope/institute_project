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
