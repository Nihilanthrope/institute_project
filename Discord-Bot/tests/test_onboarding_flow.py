import ast
from pathlib import Path

SOURCE = Path(__file__).parents[1] / "bot.py"


def test_onboarding_constants_cover_safe_roles_and_games():
    tree = ast.parse(SOURCE.read_text())
    names = {node.targets[0].id for node in tree.body if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)}
    assert "ONBOARDING_MANAGED_ROLES" in names
    assert "ONBOARDING_STEPS" in names
    assert "GAME_ARTWORK" in names


def test_onboarding_does_not_manage_staff_roles():
    tree = ast.parse(SOURCE.read_text())
    source = ast.unparse(tree)
    for role in ("Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator", "Support"):
        assert role not in source.split("ONBOARDING_MANAGED_ROLES", 1)[-1].split("ONBOARDING_STEPS", 1)[0]


def test_game_artwork_has_existing_game_roles():
    tree = ast.parse(SOURCE.read_text())
    source = ast.unparse(tree)
    assert "Valorant" in source and "Minecraft" in source and "GTA V" in source


def test_profile_answers_are_not_public_message_content():
    tree = ast.parse(SOURCE.read_text())
    source = ast.unparse(tree)
    assert "ephemeral=True" in source


def test_role_mapping_is_safe_and_includes_verified_and_games():
    import bot

    selected = bot.build_onboarding_roles({
        "games": ["Valorant", "Minecraft"],
        "interests": ["Developer", "AI / ML"],
        "purpose": ["Gaming", "Teammates"],
        "notifications": ["Announcements"],
    })
    assert {"Verified", "Valorant", "Minecraft", "Developer", "AI / ML", "Gaming", "Teammates", "Announcements"} <= selected
    assert not ({"Founder", "Administrator", "Moderator", "Client"} & selected)
