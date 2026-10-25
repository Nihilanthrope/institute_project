import unittest

from bot import ROLE_PERMISSION_POLICY, CATEGORY_ACCESS_POLICY, GAME_ROLES, CHANNEL_LOCK_POLICY


class StrictRoleAccessTests(unittest.TestCase):
    def test_only_top_three_are_administrators(self):
        self.assertEqual(
            [name for name, perms in ROLE_PERMISSION_POLICY.items() if perms.administrator],
            ["Founder", "Co-Founder", "Administrator"],
        )

    def test_public_and_game_roles_have_no_elevated_permissions(self):
        for name in ["Developer", "Designer", "Content Creator", "Client", "Verified", "Member", *GAME_ROLES]:
            perms = ROLE_PERMISSION_POLICY[name]
            self.assertFalse(perms.administrator, name)
            self.assertFalse(perms.manage_guild, name)
            self.assertFalse(perms.manage_channels, name)
            self.assertFalse(perms.manage_roles, name)
            self.assertFalse(perms.ban_members, name)
            self.assertFalse(perms.kick_members, name)

    def test_private_access_groups_are_strict(self):
        self.assertEqual(CATEGORY_ACCESS_POLICY["╭・𝗖𝗟𝗜𝗘𝗡𝗧 𝗛𝗨𝗕"], {"Client", "Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Support"})
        self.assertEqual(CATEGORY_ACCESS_POLICY["╭・𝗧𝗘𝗔𝗠 𝗛𝗤"], {"Developer", "Designer", "Content Creator", "Founder", "Co-Founder", "Administrator", "Operations", "Manager"})
        self.assertEqual(CATEGORY_ACCESS_POLICY["╭・𝗢𝗣𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦"], {"Founder", "Co-Founder", "Administrator", "Operations"})
        self.assertEqual(CATEGORY_ACCESS_POLICY["╭・𝗔𝗣𝗣𝗦 & 𝗧𝗢𝗢𝗟𝗦"], {"Founder", "Co-Founder", "Administrator", "Operations"})

    def test_bot_sections_are_restricted_and_consolidated(self):
        self.assertEqual(
            CATEGORY_ACCESS_POLICY["╭・𝗕𝗢𝗧・𝗟𝗢𝗚𝗦"],
            {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator", "Support"},
        )
        old_categories = {"╭・𝗪𝗜𝗖𝗞", "╭・𝗧𝗜𝗖𝗞𝗘𝗧・𝗧𝗢𝗢𝗟", "╭・𝗦𝗧𝗔𝗧𝗕𝗢𝗧", "╭・𝗔𝗥𝗖𝗔𝗡𝗘", "╭・𝗫𝗘𝗡𝗢𝗡", "╭・𝗖𝗔𝗥𝗟・𝗕𝗢𝗧"}
        self.assertTrue(old_categories.isdisjoint(CATEGORY_ACCESS_POLICY))

    def test_read_only_channels_are_explicit(self):
        self.assertEqual(
            CHANNEL_LOCK_POLICY["・𝗥𝘂𝗹𝗲𝘀"]["mode"],
            "public_read_only",
        )
        self.assertEqual(
            CHANNEL_LOCK_POLICY["・𝗔𝗻𝗻𝗼𝘂𝗻𝗰𝗲𝗺𝗲𝗻𝘁𝘀"]["mode"],
            "public_read_only",
        )
        self.assertEqual(
            CHANNEL_LOCK_POLICY["・𝗧𝗶𝗰𝗸𝗲𝘁・𝗣𝗮𝗻𝗲𝗹"]["mode"],
            "public_read_only_bot_write",
        )

    def test_sensitive_logs_are_bot_write_only(self):
        for name in ["・𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆・𝗟𝗼𝗴𝘀", "・𝗔𝗻𝘁𝗶𝗥𝗮𝗶𝗱・𝗟𝗼𝗴𝘀", "・𝗖𝗮𝗿𝗹・𝗟𝗼𝗴𝘀", "・𝗕𝗮𝗰𝗸𝘂𝗽𝘀"]:
            self.assertEqual(CHANNEL_LOCK_POLICY[name]["mode"], "restricted_bot_write")


if __name__ == "__main__":
    unittest.main()


def test_support_cannot_inherit_destructive_moderation_power():
    from moderation import MODERATION_ACTION_ROLES

    assert "Support" not in MODERATION_ACTION_ROLES["kick"]
    assert "Support" not in MODERATION_ACTION_ROLES["ban"]
    assert "Support" not in MODERATION_ACTION_ROLES["timeout"]
    assert "Support" not in MODERATION_ACTION_ROLES["warn"]


def test_game_hubs_are_role_exclusive():
    from bot import build_game_hub_policy

    policy = build_game_hub_policy("Valorant", ["Valorant", "Minecraft", "Member", "Moderator"])
    assert policy["everyone_view"] is False
    assert policy["allowed_game_role"] == "Valorant"
    assert policy["blocked_game_roles"] == {"Minecraft"}
    assert "Member" in policy["blocked_non_game_roles"]
    assert "Moderator" not in policy["blocked_non_game_roles"]


def test_game_hub_channel_policy_matches_category_policy():
    from bot import build_game_hub_channel_policy

    policy = build_game_hub_channel_policy("Valorant", ["Valorant", "Minecraft"])
    assert policy["everyone_view"] is False
    assert policy["game_role_view"] is True
    assert policy["other_game_roles_view"] is False


def test_game_hub_overwrites_are_explicitly_role_scoped():
    import discord
    from bot import build_game_hub_overwrites

    everyone = discord.Object(id=1)
    valorant = discord.Object(id=2)
    minecraft = discord.Object(id=3)
    overwrites = build_game_hub_overwrites(everyone, valorant, {minecraft}, set())
    assert overwrites[everyone].view_channel is False
    assert overwrites[valorant].view_channel is True
    assert overwrites[minecraft].view_channel is False
