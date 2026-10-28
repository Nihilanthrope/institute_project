import asyncio
from types import SimpleNamespace

import discord
import bot
from verify_full_upgrade import build_report, readiness_lines, read_onboarding_enabled


def test_server_purge_predicate_preserves_pinned_messages():
    from types import SimpleNamespace
    pinned = SimpleNamespace(pinned=True)
    normal = SimpleNamespace(pinned=False)
    assert bot.should_delete_server_message(pinned) is False
    assert bot.should_delete_server_message(normal) is True


def test_server_clean_command_is_registered():
    assert bot.tree.get_command("server-clean") is not None


def test_server_clean_uses_partial_message_compatible_delete():
    class FakeMessage:
        pinned = False

        async def delete(self):
            self.deleted = True

    message = FakeMessage()
    asyncio.run(bot.delete_server_message(message))
    assert message.deleted is True


def test_denied_global_check_uses_followup_when_interaction_is_already_acknowledged():
    class FakeResponse:
        def is_done(self):
            return True

    class FakeFollowup:
        def __init__(self):
            self.sent = 0

        async def send(self, *args, **kwargs):
            self.sent += 1

    member = SimpleNamespace(roles=[SimpleNamespace(name="Member")])
    response = FakeResponse()
    followup = FakeFollowup()
    interaction = SimpleNamespace(user=member, response=response, followup=followup)
    assert asyncio.run(bot._rupzha_bot_global_check(interaction)) is False
    assert followup.sent == 1


def test_moderation_access_accepts_server_owner_without_named_staff_role():
    from types import SimpleNamespace

    owner = SimpleNamespace(id=42, roles=[])
    guild = SimpleNamespace(owner_id=42)
    interaction = SimpleNamespace(user=owner, guild=guild)
    assert bot.can_use_staff_command(interaction, {"Founder", "Administrator"}) is True


def test_moderation_access_accepts_manage_messages_permission():
    from types import SimpleNamespace

    member = SimpleNamespace(
        id=42,
        roles=[],
        guild_permissions=SimpleNamespace(manage_messages=True, administrator=False),
    )
    guild = SimpleNamespace(owner_id=99)
    interaction = SimpleNamespace(user=member, guild=guild)
    assert bot.can_use_staff_command(interaction, {"Founder", "Administrator"}, require="manage_messages") is True


def test_named_staff_role_is_authorized_even_without_ui_permission_flag():
    from types import SimpleNamespace

    member = SimpleNamespace(
        id=42,
        roles=[SimpleNamespace(name="Moderator")],
        guild_permissions=SimpleNamespace(manage_messages=False, administrator=False),
    )
    guild = SimpleNamespace(owner_id=99)
    interaction = SimpleNamespace(user=member, guild=guild)
    assert bot.can_use_staff_command(interaction, {"Moderator"}, require="manage_messages") is True


def test_moderation_access_rejects_member_without_role_or_permission():
    from types import SimpleNamespace

    member = SimpleNamespace(
        id=42,
        roles=[],
        guild_permissions=SimpleNamespace(manage_messages=False, administrator=False),
    )
    guild = SimpleNamespace(owner_id=99)
    interaction = SimpleNamespace(user=member, guild=guild)
    assert bot.can_use_staff_command(interaction, {"Founder", "Administrator"}, require="manage_messages") is False


def test_server_clean_command_is_fail_closed_to_manage_messages_or_owner():
    from types import SimpleNamespace

    member = SimpleNamespace(
        id=42,
        roles=[],
        guild_permissions=SimpleNamespace(manage_messages=False, administrator=False),
    )
    guild = SimpleNamespace(owner_id=99)
    interaction = SimpleNamespace(user=member, guild=guild)
    assert bot.can_use_staff_command(interaction, {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator"}, require="manage_messages") is False


def test_bot_access_is_limited_to_founder_and_cofounder():
    from types import SimpleNamespace

    founder = SimpleNamespace(roles=[SimpleNamespace(name="Founder")])
    cofounder = SimpleNamespace(roles=[SimpleNamespace(name="Co-Founder")])
    administrator = SimpleNamespace(roles=[SimpleNamespace(name="Administrator")])
    moderator = SimpleNamespace(roles=[SimpleNamespace(name="Moderator")])
    member = SimpleNamespace(roles=[SimpleNamespace(name="Member")])

    assert bot.can_use_rupzha_bot(founder) is True
    assert bot.can_use_rupzha_bot(cofounder) is True
    assert bot.can_use_rupzha_bot(administrator) is False
    assert bot.can_use_rupzha_bot(moderator) is False
    assert bot.can_use_rupzha_bot(member) is False


def test_bot_access_requires_exact_highest_role_names_not_position_only():
    from types import SimpleNamespace

    impostor = SimpleNamespace(roles=[SimpleNamespace(name="Administrator", position=99)])
    assert bot.can_use_rupzha_bot(impostor) is False


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


def test_welcome_event_personalizes_members_without_duplicate_gateway_instances():
    source = open("bot.py", encoding="utf-8").read()
    assert "member.display_name} — you’re officially in" in source
    assert "member.mention} — you’re officially in" not in source
    assert "fcntl.LOCK_EX | fcntl.LOCK_NB" in source
    assert "refusing duplicate gateway process" in source


def test_game_hub_policy_requires_matching_role_and_hides_other_game_roles():
    from types import SimpleNamespace
    from verify_full_upgrade import check_game_hub_policy

    class Overwrite:
        def __init__(self, view): self.view_channel = view

    class Category:
        def __init__(self): self.overrides = {}
        def overwrites_for(self, role): return self.overrides.get(role, Overwrite(None))

    everyone = object(); valorant = object(); minecraft = object()
    valorant_category = Category()
    valorant_category.overrides[everyone] = Overwrite(False)
    valorant_category.overrides[valorant] = Overwrite(True)
    valorant_category.overrides[minecraft] = Overwrite(False)
    minecraft_category = Category()
    minecraft_category.overrides[everyone] = Overwrite(False)
    minecraft_category.overrides[minecraft] = Overwrite(True)
    minecraft_category.overrides[valorant] = Overwrite(False)
    roles = {"Valorant": valorant, "Minecraft": minecraft}
    categories = {
        "╭・𝗚𝗔𝗠𝗘・VALORANT": valorant_category,
        "╭・𝗚𝗔𝗠𝗘・𝗠𝗜𝗡𝗘𝗖𝗥𝗔𝗙𝗧": minecraft_category,
    }
    failures = check_game_hub_policy(everyone, roles, categories, ["Valorant", "Minecraft"])
    assert failures == []


def test_unapproved_role_hardening_removes_escalation_and_preserves_basic_access():
    permissions = discord.Permissions(
        administrator=True, manage_guild=True, manage_roles=True, manage_channels=True,
        manage_webhooks=True, kick_members=True, ban_members=True, moderate_members=True,
        mention_everyone=True, manage_messages=True, send_messages=True, view_channel=True,
    )

    hardened = bot.harden_unapproved_role_permissions(permissions)

    for permission in (
        "administrator", "manage_guild", "manage_roles", "manage_channels", "manage_webhooks",
        "kick_members", "ban_members", "moderate_members", "mention_everyone", "manage_messages",
    ):
        assert getattr(hardened, permission) is False
    assert hardened.send_messages is True
    assert hardened.view_channel is True


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
    assert set(bot.THIRD_PARTY_BOT_CHANNELS) == {"OwO", "Pokétwo", "Koya"}
    assert bot.THIRD_PARTY_BOT_CHANNELS["OwO"] == "🤖・・𝗢𝘄𝗢"
    assert bot.THIRD_PARTY_BOT_CHANNELS["Pokétwo"] == "🎮・・𝗣𝗼𝗸𝗲𝘁𝘄𝗼"
    assert bot.THIRD_PARTY_BOT_CHANNELS["Koya"] == "🌸・・𝗞𝗼𝘆𝗮"
    assert bot.THIRD_PARTY_BOT_CHANNEL_POLICIES["OwO"]["bot_role"] == "OwO"
    assert bot.THIRD_PARTY_BOT_CHANNEL_POLICIES["Pokétwo"]["bot_role"] == "Pokétwo"
    assert bot.THIRD_PARTY_BOT_CHANNEL_POLICIES["Koya"]["bot_role"] == "Koya"


def test_third_party_bot_channels_are_unique():
    assert len(set(bot.THIRD_PARTY_BOT_CHANNELS.values())) == 3


def test_third_party_bots_cannot_write_in_each_others_channels():
    for bot_name, own_channel in bot.THIRD_PARTY_BOT_CHANNELS.items():
        for other_name, other_channel in bot.THIRD_PARTY_BOT_CHANNELS.items():
            if bot_name == other_name:
                continue
            policy = bot.build_third_party_bot_overwrite(bot_name, own_channel, other_channel)
            assert policy["allowed"] is False
            assert policy["send_messages"] is False
            assert policy["use_application_commands"] is False


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
    own = bot.build_third_party_bot_overwrite("OwO", bot.BOT_COMMAND_CHANNEL_NAME, bot.BOT_COMMAND_CHANNEL_NAME)
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



def test_bot_channel_policy_keeps_shared_channel_for_other_utility_bots():
    expected_bots = {
        "Dank Memer", "Diva", "Freebee", "Hazy", "Mimu",
        "Poké-Name", "Sapphire", "Tune 🌷", "Word Chain Bot Indently",
    }
    assert expected_bots <= set(bot.BOT_COMMAND_CHANNELS_BY_BOT)
    assert all(bot.BOT_COMMAND_CHANNELS_BY_BOT[name] == bot.BOT_COMMAND_CHANNEL_NAME for name in expected_bots)


def test_dedicated_bot_roles_cannot_keep_administrator_power():
    permissions = discord.Permissions(administrator=True, manage_roles=True, send_messages=True)
    hardened = bot.permissions_for_third_party_bot_role("OwO", permissions)
    assert hardened.administrator is False
    assert hardened.manage_roles is False
    assert hardened.send_messages is True


def test_dedicated_bot_role_hardening_is_limited_to_member_facing_bots():
    permissions = discord.Permissions(administrator=True)
    assert bot.permissions_for_third_party_bot_role("OwO", permissions).administrator is False
    assert bot.permissions_for_third_party_bot_role("Pokétwo", permissions).administrator is False
    assert bot.permissions_for_third_party_bot_role("Koya", permissions).administrator is False
    assert bot.permissions_for_third_party_bot_role("Mimu", permissions).administrator is True


def test_third_party_bot_message_policy_deletes_owo_outside_dedicated_channel():
    assert bot.third_party_bot_message_allowed(408785106942164992, 1564050781307670629) is True
    assert bot.third_party_bot_message_allowed(408785106942164992, 1564050781307670629 + 1) is False


def test_owo_application_command_scope_allows_only_its_channel():
    scope = bot.build_application_command_scope(1554830636454514708, 1564050781307670629)
    assert scope == [
        {"id": "1554830636454514708", "type": 1, "permission": False},
        {"id": "1564050781307670629", "type": 3, "permission": True},
    ]


def test_dedicated_bot_channel_names_are_canonical():
    assert bot.DEDICATED_BOT_CHANNELS == {
        "OwO": "🤖・・𝗢𝘄𝗢",
        "Pokétwo": "🎮・・𝗣𝗼𝗸𝗲𝘁𝘄𝗼",
        "Koya": "🌸・・𝗞𝗼𝘆𝗮",
    }


def test_ticket_panel_marker_check_handles_messages_without_footer_text():
    from types import SimpleNamespace
    message = SimpleNamespace(content="", embeds=[SimpleNamespace(footer=SimpleNamespace(text=None))])
    assert bot.ticket_panel_has_marker(message, "RUPZHA_TICKET_PANEL_V1") is False


def test_ticket_lifecycle_has_claim_priority_escalate_close_and_archive_controls():
    import inspect
    import bot

    source = inspect.getsource(bot.TicketControlsView)
    assert "Claim" in source
    assert "Priority" in source
    assert "Escalate" in source
    assert "TicketCloseModal" in source
    assert "custom_id=f\"rupzha:tickets:{action}:{self.ticket_id}\"" in source


def test_ticket_close_generates_transcript_and_archives_with_retention():
    import inspect
    import bot

    source = inspect.getsource(bot.TicketCloseModal.on_submit)
    assert "write_ticket_transcript" in source
    assert "archive_closed_ticket" in source
    assert "24 hours" in source


def test_ticket_lifecycle_task_only_deletes_archived_tickets_with_transcripts():
    import inspect
    import bot

    source = inspect.getsource(bot.ticket_lifecycle_loop)
    assert "status='archived'" in source
    assert "transcript_path" in source
    assert "channel.delete" in source


def test_ticket_category_selection_is_ephemeral_and_does_not_edit_public_panel():
    import inspect
    source = inspect.getsource(bot.TicketPanelView.choose)
    assert "send_message" in source
    assert "ephemeral=True" in source
    assert "edit_message" not in source


def test_bot_command_layout_accepts_shared_and_three_dedicated_channels():
    from types import SimpleNamespace
    children = [
        SimpleNamespace(name=bot.BOT_COMMAND_CHANNEL_NAME),
        *(SimpleNamespace(name=name) for name in bot.DEDICATED_BOT_CHANNELS.values()),
    ]
    assert bot.check_bot_command_layout(children) == []


def test_game_hub_policy_only_blocks_other_selected_game_roles():
    policy = bot.build_game_hub_policy("Valorant", {"Valorant", "Minecraft", "Member", "Developer"})
    assert policy["blocked_game_roles"] == {"Minecraft"}


def test_public_start_here_channels_have_canonical_emoji_names():
    assert bot.PUBLIC_CHANNELS == {
        "welcome": "👋・・𝗪𝗲𝗹𝗰𝗼𝗺𝗲",
        "rules": "📜・・𝗥𝘂𝗹𝗲𝘀",
        "announcements": "📢・・𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁𝘀",
        "roles": "🎭・・𝗖𝗵𝗼𝗼𝘀𝗲・𝗥𝗼𝗹𝗲𝘀",
        "how": "❓・・𝗛𝗼𝘄・𝗜𝘁・𝗪𝗼𝗿𝗸𝘀",
        "faq": "❔・・𝗙𝗔𝗤",
    }


def test_welcome_board_is_static_and_graphical():
    embed = bot.build_static_welcome_embed()
    assert embed.title == "✦・𝗪𝗘𝗟𝗖𝗢𝗠𝗘・✦"
    assert embed.image.url == "attachment://rupzha-welcome.gif"
    assert "RupZha" in embed.description


def test_member_welcome_personalizes_with_mention():
    member = SimpleNamespace(
        display_name="RandomUser",
        mention="<@999999999>",
        guild=SimpleNamespace(member_count=22),
        display_avatar=SimpleNamespace(url=None),
    )
    embed = bot.build_welcome_embed(member)
    assert member.display_name in embed.description
    assert member.mention in embed.description


def test_bot_role_hardening_removes_admin_but_preserves_other_permissions():
    import discord
    role = SimpleNamespace(managed=False, permissions=discord.Permissions(administrator=True, manage_messages=True))
    hardened = bot.harden_third_party_bot_permissions(role.permissions)
    assert hardened.administrator is False
    assert hardened.manage_messages is True


def test_managed_bot_security_audit_flags_uneditable_admin_roles():
    import discord
    admin_role = SimpleNamespace(managed=True, permissions=discord.Permissions(administrator=True))
    safe_role = SimpleNamespace(managed=True, permissions=discord.Permissions.none())
    failures = __import__("verify_full_upgrade").managed_utility_bot_security_failures(
        {"Hazy": admin_role, "Tune 🌷": safe_role}, {"Hazy", "Tune 🌷"}
    )
    assert failures == ["bot-role:Hazy:managed-dangerous=administrator"]

def test_every_bot_own_channel_is_fully_operational():
    own = bot.build_universal_bot_overwrite("Mimu", "🤖・・𝗠𝗶𝗺𝘂", "🤖・・𝗠𝗶𝗺𝘂")
    assert all(own[k] is True for k in ("view_channel", "read_message_history", "send_messages", "send_messages_in_threads", "use_application_commands", "add_reactions"))


def test_special_bot_keeps_only_its_functional_channels_writable():
    assert bot.SPECIAL_BOT_CHANNEL_POLICIES["Wick"] == {"📋・・𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆・𝗟𝗼𝗴𝘀", "📋・・𝗔𝗻𝘁𝗶𝗥𝗮𝗶𝗱・𝗟𝗼𝗴𝘀"}
    assert bot.SPECIAL_BOT_CHANNEL_POLICIES["Ticket Tool"] == {"🎫・・𝗧𝗶𝗰𝗸𝗲𝘁・𝗣𝗮𝗻𝗲𝗹"}


def test_bot_channel_policy_resolves_canonical_names_case_insensitively():
    assert bot.bot_allowed_channels_for_member("Carl-bot", 1) == bot.SPECIAL_BOT_CHANNEL_POLICIES["carl-bot"]
    assert bot.bot_allowed_channels_for_member("Koya", 2) == {bot.DEDICATED_BOT_CHANNELS["Koya"]}


def test_private_ticket_rooms_are_separate_from_public_ticket_panel():
    assert bot.TICKET_ROOMS_CATEGORY == "╭・𝗧𝗜𝗖𝗞𝗘𝗧・𝗥𝗢𝗢𝗠𝗦"
    assert bot.TICKET_ROOMS_CATEGORY in bot.CATEGORY_ACCESS_POLICY
    assert "╭・𝗧𝗜𝗖𝗞𝗘𝗧・𝗧𝗢𝗢𝗟" not in bot.CATEGORY_ACCESS_POLICY
    ticket_policy = bot.channel_policy_for_name("🎫・・𝗧𝗶𝗰𝗸𝗲𝘁・𝗣𝗮𝗻𝗲𝗹", bot.CHANNEL_LOCK_POLICY)
    assert "Ticket Tool" in ticket_policy["bot_roles"]
    assert "RupZha" in ticket_policy["bot_roles"]


def test_channel_policy_matches_emoji_prefixed_names():
    assert bot.channel_policy_for_name("🎫・・𝗧𝗶𝗰𝗸𝗲𝘁・𝗣𝗮𝗻𝗲𝗹", bot.CHANNEL_LOCK_POLICY) == {
        "mode": "public_read_only_bot_write", "bot_roles": ["Ticket Tool", "RupZha"]
    }
    assert bot.channel_policy_for_name("📋・・𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆・𝗟𝗼𝗴𝘀", bot.CHANNEL_LOCK_POLICY) == {
        "mode": "restricted_bot_write", "bot_roles": ["Wick"]
    }


def test_game_hub_audit_matches_math_bold_category_names():
    from verify_full_upgrade import check_game_hub_policy

    class Overwrite:
        def __init__(self, view): self.view_channel = view

    class Category:
        def __init__(self): self.overrides = {}
        def overwrites_for(self, role): return self.overrides.get(role, Overwrite(None))

    everyone, valorant = object(), object()
    category = Category()
    category.overrides[everyone] = Overwrite(True)
    category.overrides[valorant] = Overwrite(True)
    failures = check_game_hub_policy(
        everyone, {"Valorant": valorant}, {"╭・𝗚𝗔𝗠𝗘・𝗩𝗔𝗟𝗢𝗥𝗔𝗡𝗧": category}, ["Valorant"]
    )
    assert "game:Valorant:everyone" in failures


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


def test_legacy_bot_prefix_policy_allows_only_the_public_bot_command_channel():
    assert bot.BOT_COMMAND_CHANNEL_NAME == "🤖・・𝗕𝗼𝘁・𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀"
    assert bot.legacy_bot_prefix_is_blocked("owo cash", "💬・・𝗚𝗲𝗻𝗲𝗿𝗮𝗹") is True
    assert bot.legacy_bot_prefix_is_blocked("owo cash", bot.BOT_COMMAND_CHANNEL_NAME) is False
    assert bot.legacy_bot_prefix_is_blocked("p!catch pikachu", "💬・・𝗚𝗲𝗻𝗲𝗿𝗮𝗹") is True
    assert bot.legacy_bot_prefix_is_blocked("owo that's cute", "💬・・𝗚𝗲𝗻𝗲𝗿𝗮𝗹") is False

def test_rupzha_bot_role_has_no_administrator_and_only_required_bot_power():
    perms = bot.ROLE_PERMISSION_POLICY["Rupzha Bot"]
    assert perms.administrator is False
    assert perms.manage_channels is True
    assert perms.manage_roles is True
    assert perms.manage_messages is True
    assert perms.manage_threads is True
    assert perms.kick_members is True
    assert perms.ban_members is True
    assert perms.moderate_members is True
    assert perms.manage_guild is False
