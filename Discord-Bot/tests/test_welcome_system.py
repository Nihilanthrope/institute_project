import unittest
from types import SimpleNamespace

import discord

from bot import WELCOME, WELCOME_GIF_PATH, build_welcome_embed, build_static_welcome_embed, find_public_text_channel, welcome_panel_file, is_static_welcome_message


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
        self.assertIn(member.display_name, embed.description)
        self.assertIn(member.mention, embed.description)
        self.assertIn("42", embed.description)
        self.assertIn(rules.mention, embed.description)
        self.assertIn(roles.mention, embed.description)
        self.assertGreaterEqual(len(embed.fields), 4)
        self.assertEqual(embed.color.value, 0xFF4F6D)
        field_names = [field.name for field in embed.fields]
        self.assertEqual(field_names, ["01 · 𝗦𝗧𝗔𝗥𝗧 𝗛𝗘𝗥𝗘", "02 · 𝗣𝗜𝗖𝗞 𝗬𝗢𝗨𝗥 𝗥𝗢𝗟𝗘𝗦", "03 · 𝗠𝗘𝗘𝗧 𝗧𝗛𝗘 𝗖𝗢𝗠𝗠𝗨𝗡𝗜𝗧𝗬", "04 · 𝗛𝗔𝗩𝗘 𝗙𝗨𝗡"])
        self.assertIn("your space to play", embed.footer.text)

    def test_member_welcome_uses_static_gif_and_normal_avatar(self):
        member = SimpleNamespace(
            id=789,
            mention="<@789>",
            display_name="New Member",
            guild=SimpleNamespace(member_count=43),
            display_avatar=SimpleNamespace(url="https://cdn.discordapp.com/avatars/789/test.png"),
        )

        embed = build_welcome_embed(member)

        self.assertEqual(embed.image.url, "attachment://rupzha-welcome.gif")
        self.assertEqual(embed.thumbnail.url, "https://cdn.discordapp.com/avatars/789/test.png")

    def test_rupzha_welcome_gif_asset_is_animated_background(self):
        self.assertTrue(WELCOME_GIF_PATH.is_file())
        self.assertGreater(WELCOME_GIF_PATH.stat().st_size, 100_000)
        import subprocess
        result = subprocess.run(
            ["identify", "-format", "%n %wx%h", str(WELCOME_GIF_PATH)],
            check=True, capture_output=True, text=True,
        )
        import re
        match = re.search(r"(\d+)\s+(600x338)", result.stdout)
        self.assertIsNotNone(match)
        self.assertGreater(int(match.group(1)), 1)
        self.assertEqual(match.group(2), "600x338")

    def test_static_welcome_message_detection_does_not_match_personalized_avatar_message(self):
        static = SimpleNamespace(
            author=SimpleNamespace(id=1),
            content="",
            pinned=True,
            embeds=[SimpleNamespace(
                title="✦・𝗪𝗘𝗟𝗖𝗢𝗠𝗘・✦",
                thumbnail=None,
                image=SimpleNamespace(url="attachment://rupzha-welcome.gif"),
            )],
            attachments=[SimpleNamespace(filename="rupzha-welcome.gif")],
        )
        personalized = SimpleNamespace(
            author=SimpleNamespace(id=1),
            content="",
            pinned=False,
            embeds=[SimpleNamespace(
                title="✦ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗨𝗣𝗭𝗛𝗔 ✦",
                thumbnail=SimpleNamespace(url="https://cdn.discordapp.com/avatars/789/test.png"),
                image=SimpleNamespace(url="attachment://rupzha-welcome.gif"),
            )],
            attachments=[SimpleNamespace(filename="rupzha-welcome.gif")],
        )
        self.assertTrue(is_static_welcome_message(static))
        self.assertFalse(is_static_welcome_message(personalized))
        legacy_personalized = SimpleNamespace(
            author=SimpleNamespace(id=1), content="", pinned=False,
            embeds=[SimpleNamespace(
                title="✦ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗨𝗣𝗭𝗛𝗔 ✦", thumbnail=None,
                image=SimpleNamespace(url="attachment://rupzha-welcome.gif"),
            )], attachments=[],
        )
        self.assertTrue(is_static_welcome_message(legacy_personalized))

    def test_builds_when_optional_channels_are_missing(self):
        member = SimpleNamespace(
            mention="<@456>",
            display_name="New Member",
            guild=SimpleNamespace(member_count=None),
        )

        embed = build_welcome_embed(member)

        self.assertEqual(embed.title, "✦ 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗧𝗢 𝗥𝗨𝗣𝗭𝗛𝗔 ✦")
        self.assertIn(member.display_name, embed.description)
        self.assertIn(member.mention, embed.description)
        self.assertIn("#・𝗖𝗵𝗼𝗼𝘀𝗲・𝗥𝗼𝗹𝗲𝘀", embed.description)
        self.assertIn("#・𝗥𝘂𝗹𝗲𝘀", embed.description)

    def test_static_welcome_panel_embed_displays_graphical_gif(self):
        embed = build_static_welcome_embed()
        self.assertEqual(embed.image.url, "attachment://rupzha-welcome.gif")
        self.assertEqual(embed.color.value, 0xFF1F3D)

    def test_static_welcome_panel_uses_graphical_gif_asset(self):
        welcome_file = welcome_panel_file()
        self.assertEqual(welcome_file.filename, "rupzha-welcome.gif")

    def test_static_welcome_matches_server_panel_style(self):
        self.assertIn("<!-- RUPZHA_WELCOME_PANEL_V2 -->", WELCOME)
        self.assertIn("✦・𝗪𝗘𝗟𝗖𝗢𝗠𝗘・✦", WELCOME)
        self.assertIn("01 · 𝗥𝗘𝗔𝗗", WELCOME)
        self.assertIn("02 · 𝗖𝗛𝗢𝗢𝗦𝗘", WELCOME)
        self.assertIn("03 · 𝗝𝗢𝗜𝗡 𝗜𝗡", WELCOME)
        self.assertIn("04 · 𝗛𝗔𝗩𝗘 𝗙𝗨𝗡", WELCOME)

    def test_public_channel_lookup_accepts_emoji_prefixed_channel_names(self):
        desired = "・𝗪𝗲𝗹𝗰𝗼𝗺𝗲"
        channels = [SimpleNamespace(name="👋・・𝗪𝗲𝗹𝗰𝗼𝗺𝗲", id=99)]
        self.assertEqual(find_public_text_channel(channels, desired).id, 99)


if __name__ == "__main__":
    unittest.main()
