from community import CommunityService, level_for_xp
from storage import Database


def test_level_thresholds_are_deterministic():
    assert level_for_xp(0) == 1
    assert level_for_xp(99) == 1
    assert level_for_xp(100) == 2
    assert level_for_xp(299) == 2
    assert level_for_xp(300) == 3


def test_award_xp_persists_profile(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    service = CommunityService(db)
    assert service.award_xp(123, 150) == 150
    assert service.award_xp(123, 50) == 200
    profile = service.get_profile(123)
    assert profile["xp"] == 200
    assert profile["level"] == 2


def test_message_xp_cooldown_is_conservative(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    service = CommunityService(db, xp_per_message=20, cooldown_seconds=60)
    assert service.record_message(123, now=100.0) == 20
    assert service.record_message(123, now=120.0) == 0
    assert service.record_message(123, now=161.0) == 20


def test_suggestion_and_event_persistence(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    service = CommunityService(db)
    suggestion_id = service.create_suggestion(123, "Add a weekend tournament")
    event_id = service.create_event(456, "RupZha Game Night", "2026-11-01T20:00:00+05:30")
    assert service.get_suggestion(suggestion_id)["content"] == "Add a weekend tournament"
    assert service.get_event(event_id)["title"] == "RupZha Game Night"


def test_event_creation_requires_staff(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    service = CommunityService(db)
    assert service.can_create_event({"Member"}) is False
    assert service.can_create_event({"Moderator"}) is True
