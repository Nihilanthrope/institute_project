from operations import STAFF_ROLES, build_client_status_embed, can_edit_project, can_view_project, create_internal_case, get_project_status, sanitize_public_text, set_project_status
from storage import Database


def test_client_can_view_but_not_edit_project(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    set_project_status(db, "RZ-01", "In Progress", "Website build")
    assert can_view_project({"Client"}) is True
    assert can_edit_project({"Client"}) is False
    assert can_edit_project({"Manager"}) is True
    assert get_project_status(db, "RZ-01")["status"] == "In Progress"


def test_public_member_cannot_view_private_project(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    set_project_status(db, "RZ-02", "Review", "Private")
    assert can_view_project({"Member"}) is False
    assert can_view_project({"Client"}) is True


def test_public_status_text_strips_private_urls_and_emails():
    sanitized = sanitize_public_text("Build review: secret@example.com https://private.example/path")
    assert "secret@example.com" not in sanitized
    assert "https://private.example/path" not in sanitized


def test_internal_case_is_staff_only_and_sanitized(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    assert create_internal_case(db, 123, {"Member"}, "client email: secret@example.com") is None
    case_id = create_internal_case(db, 123, {"Operations"}, "Client payment follow-up\nhttps://private.example")
    assert case_id is not None
    assert "secret@example.com" not in build_client_status_embed(db, "RZ-01", {"Client"}).description
