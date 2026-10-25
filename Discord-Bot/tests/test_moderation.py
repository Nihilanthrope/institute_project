import pytest

from moderation import JoinGuard, can_moderate, get_recent_cases, is_staff, record_case
from storage import Database


class FakeRole:
    def __init__(self, position, name=""):
        self.position = position
        self.name = name


class FakeMember:
    def __init__(self, roles, *, bot=False):
        self.roles = roles
        self.bot = bot

    @property
    def top_role(self):
        return max(self.roles, key=lambda role: role.position)


def test_staff_gate_uses_named_staff_roles():
    assert is_staff(FakeMember([FakeRole(1, "Member")]), {"Moderator"}) is False
    assert is_staff(FakeMember([FakeRole(1, "Moderator")]), {"Moderator"}) is True


def test_moderation_rejects_equal_or_higher_target():
    actor = FakeMember([FakeRole(5)])
    equal = FakeMember([FakeRole(5)])
    lower = FakeMember([FakeRole(4)])
    assert can_moderate(actor, lower) is True
    assert can_moderate(actor, equal) is False
    assert can_moderate(actor, actor) is False


def test_warning_cases_persist_and_increment_case_number(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    first = record_case(db, 10, 20, 30, "warn", "first")
    second = record_case(db, 10, 20, 30, "warn", "second")
    assert first == 1
    assert second == 2
    assert [row["reason"] for row in get_recent_cases(db, 10, 20)] == ["second", "first"]


def test_join_guard_only_flags_conservative_burst():
    guard = JoinGuard(window_seconds=10, threshold=5)
    assert guard.record(1, now=100.0) == []
    assert guard.record(2, now=101.0) == []
    assert guard.record(3, now=102.0) == []
    assert guard.record(4, now=103.0) == []
    assert guard.record(5, now=104.0) == [1, 2, 3, 4, 5]
    assert guard.record(6, now=120.0) == []


def test_log_security_event_uses_configured_channel_lookup():
    from moderation import security_log_channel_name

    assert security_log_channel_name({"security_log_channel": "・𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆・𝗟𝗼𝗴𝘀"}) == "・𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆・𝗟𝗼𝗴𝘀"


def test_action_specific_moderation_roles_fail_closed():
    from moderation import can_execute_moderation

    support = FakeMember([FakeRole(7, "Support")])
    moderator = FakeMember([FakeRole(10, "Moderator")])
    manager = FakeMember([FakeRole(11, "Manager")])
    target = FakeMember([FakeRole(2, "Member")])

    assert can_execute_moderation(support, target, "kick") is False
    assert can_execute_moderation(support, target, "ban") is False
    assert can_execute_moderation(moderator, target, "kick") is True
    assert can_execute_moderation(moderator, target, "ban") is False
    assert can_execute_moderation(manager, target, "kick") is False
    assert can_execute_moderation(manager, target, "ban") is False
    assert can_execute_moderation(manager, target, "unknown") is False


def test_action_specific_moderation_rejects_managed_and_owner_targets():
    from moderation import can_execute_moderation

    actor = FakeMember([FakeRole(10, "Moderator")])
    managed = FakeMember([FakeRole(2, "Bot")])
    managed.roles[0].managed = True
    target = FakeMember([FakeRole(2, "Member")])
    target.guild = type("Guild", (), {"owner_id": 99})()
    target.id = 99

    assert can_execute_moderation(actor, managed, "kick") is False
    assert can_execute_moderation(actor, target, "kick") is False
