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

    def test_bot_sections_are_restricted(self):
        self.assertEqual(CATEGORY_ACCESS_POLICY["╭・𝗪𝗜𝗖𝗞"], {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator"})
        self.assertEqual(CATEGORY_ACCESS_POLICY["╭・𝗧𝗜𝗖𝗞𝗘𝗧・𝗧𝗢𝗢𝗟"], {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Support"})
        self.assertEqual(CATEGORY_ACCESS_POLICY["╭・𝗦𝗧𝗔𝗧𝗕𝗢𝗧"], {"Founder", "Co-Founder", "Administrator", "Operations", "Manager"})
        self.assertEqual(CATEGORY_ACCESS_POLICY["╭・𝗫𝗘𝗡𝗢𝗡"], {"Founder", "Co-Founder", "Administrator"})
        self.assertEqual(CATEGORY_ACCESS_POLICY["╭・𝗖𝗔𝗥𝗟・𝗕𝗢𝗧"], {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator"})

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
