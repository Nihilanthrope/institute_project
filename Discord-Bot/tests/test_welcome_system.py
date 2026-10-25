import unittest
from types import SimpleNamespace

import discord

from bot import build_welcome_embed


class WelcomeEmbedTests(unittest.TestCase):
    def test_builds_polished_member_welcome(self):
        member = SimpleNamespace(
            mention="<@123>",
            display_name="Nihilanthrope",
            guild=SimpleNamespace(member_count=42),
        )
        rules = SimpleNamespace(mention="#・𝗥𝘂𝗹𝗲𝘀")
        roles = SimpleNamespace(mention="#・𝗖𝗵𝗼𝗼𝘀𝗲・𝗥𝗼𝗹𝗲𝘀")

        embed = build_welcome_embed(member, rules, roles)

        self.assertEqual(embed.title, "✦ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗨𝗣𝗭𝗛𝗔 ✦")
        self.assertIn(member.mention, embed.description)
        self.assertIn(member.display_name, embed.description)
        self.assertIn("42", embed.description)
        self.assertIn(rules.mention, embed.description)
        self.assertIn(roles.mention, embed.description)
        self.assertGreaterEqual(len(embed.fields), 4)
        self.assertEqual(embed.color.value, 0xFF4F6D)
        field_names = [field.name for field in embed.fields]
        self.assertEqual(field_names, ["01 · 𝗦𝗧𝗔𝗥𝗧 𝗛𝗘𝗥𝗘", "02 · 𝗣𝗜𝗖𝗞 𝗬𝗢𝗨𝗥 𝗥𝗢𝗟𝗘𝗦", "03 · 𝗠𝗘𝗘𝗧 𝗧𝗛𝗘 𝗖𝗢𝗠𝗠𝗨𝗡𝗜𝗧𝗬", "04 · 𝗛𝗔𝗩𝗘 𝗙𝗨𝗡"])
        self.assertIn("your space to play", embed.footer.text)

    def test_builds_when_optional_channels_are_missing(self):
        member = SimpleNamespace(
            mention="<@456>",
            display_name="New Member",
            guild=SimpleNamespace(member_count=None),
        )

        embed = build_welcome_embed(member)

        self.assertEqual(embed.title, "✦ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗨𝗣𝗭𝗛𝗔 ✦")
        self.assertIn(member.mention, embed.description)
        self.assertIn(member.display_name, embed.description)
        self.assertIn("#・𝗖𝗵𝗼𝗼𝘀𝗲・𝗥𝗼𝗹𝗲𝘀", embed.description)
        self.assertIn("#・𝗥𝘂𝗹𝗲𝘀", embed.description)


if __name__ == "__main__":
    unittest.main()
