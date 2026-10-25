import asyncio
from types import SimpleNamespace

import discord
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
        "╭・𝗕𝗢𝗧・𝗟𝗢𝗚𝗦",
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



def test_bot_channel_policy_has_one_canonical_channel_per_bot():
    assert bot.BOT_COMMAND_CHANNELS_BY_BOT == {
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
    assert len(set(bot.BOT_COMMAND_CHANNELS_BY_BOT.values())) == len(bot.BOT_COMMAND_CHANNELS_BY_BOT)


def test_bot_role_hardening_removes_admin_but_preserves_other_permissions():
    import discord
    role = SimpleNamespace(managed=False, permissions=discord.Permissions(administrator=True, manage_messages=True))
    hardened = bot.harden_third_party_bot_permissions(role.permissions)
    assert hardened.administrator is False
    assert hardened.manage_messages is True

def test_every_bot_own_channel_is_fully_operational():
    own = bot.build_universal_bot_overwrite("Mimu", "🤖・・𝗠𝗶𝗺𝘂", "🤖・・𝗠𝗶𝗺𝘂")
    assert all(own[k] is True for k in ("view_channel", "read_message_history", "send_messages", "send_messages_in_threads", "use_application_commands", "add_reactions"))


def test_special_bot_keeps_only_its_functional_channels_writable():
    assert bot.SPECIAL_BOT_CHANNEL_POLICIES["Wick"] == {"📋・・𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆・𝗟𝗼𝗴𝘀", "📋・・𝗔𝗻𝘁𝗶𝗥𝗮𝗶𝗱・𝗟𝗼𝗴𝘀"}
    assert bot.SPECIAL_BOT_CHANNEL_POLICIES["Ticket Tool"] == {"🎫・・𝗧𝗶𝗰𝗸𝗲𝘁・𝗣𝗮𝗻𝗲𝗹"}


def test_bot_channel_policy_resolves_canonical_names_case_insensitively():
    assert bot.bot_allowed_channels_for_member("Carl-bot", 1) == bot.SPECIAL_BOT_CHANNEL_POLICIES["carl-bot"]
    assert bot.bot_allowed_channels_for_member("Koya", 2) == {"🌸・・𝗞𝗼𝘆𝗮"}
    assert bot.bot_allowed_channels_for_member("Poké-Name", 3) == {"🤖・・𝗣𝗼𝗸𝗲・𝗡𝗮𝗺𝗲"}


def test_member_sidebar_has_one_private_integration_category_and_valid_welcome_steps():
    old_categories = {
        "╭・𝗪𝗜𝗖𝗞", "╭・𝗧𝗜𝗖𝗞𝗘𝗧・𝗧𝗢𝗢𝗟", "╭・𝗦𝗧𝗔𝗧𝗕𝗢𝗧",
        "╭・𝗔𝗥𝗖𝗔𝗡𝗘", "╭・𝗫𝗘𝗡𝗢𝗡", "╭・𝗖𝗔𝗥𝗟・𝗕𝗢𝗧",
    }
    assert "╭・𝗕𝗢𝗧・𝗟𝗢𝗚𝗦" in bot.CATEGORY_ACCESS_POLICY
    assert old_categories.isdisjoint(bot.CATEGORY_ACCESS_POLICY)
    assert "Choose・Roles" not in bot.WELCOME
    assert "Community Onboarding" in bot.WELCOME


def test_shared_member_role_overwrite_cleanup_preserves_member_specific_bot_overwrites():
    class Target:
        def __init__(self, name): self.name = name

    member_role = Target("Member")
    bot_member = Target("Dank Memer")
    restricted = discord.PermissionOverwrite(view_channel=True, send_messages=False)

    class FakeChannel:
        def __init__(self, overwrites):
            self._overwrites = dict(overwrites)
            self.removals = []

        def overwrites_for(self, target):
            return self._overwrites.get(target, discord.PermissionOverwrite())

        async def set_permissions(self, target, *, overwrite, reason):
            self.removals.append((target, overwrite, reason))
            if overwrite is None:
                self._overwrites.pop(target, None)
            else:
                self._overwrites[target] = overwrite

    channel = FakeChannel({member_role: restricted, bot_member: restricted})
    clean_channel = FakeChannel({bot_member: restricted})
    guild = SimpleNamespace(roles=[member_role], channels=[channel, clean_channel])

    removed = asyncio.run(bot.clear_shared_member_role_overwrites(guild))

    assert removed == 1
    assert member_role not in channel._overwrites
    assert channel._overwrites[bot_member] == restricted
    assert clean_channel.removals == []
