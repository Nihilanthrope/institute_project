from tickets import TicketService, build_ticket_category_overwrites, build_ticket_overwrites
from storage import Database


class FakeRole:
    def __init__(self, name):
        self.name = name


class FakeMember:
    def __init__(self, member_id, *roles):
        self.id = member_id
        self.roles = [FakeRole(name) for name in roles]


def test_expanded_ticket_taxonomy_covers_support_complaints_business_and_feedback():
    from tickets import TICKET_CATEGORIES, ticket_type_definition

    assert set(TICKET_CATEGORIES) == {"support", "complaints", "business", "feedback"}
    assert "general_support" in TICKET_CATEGORIES["support"]
    assert "security_privacy" in TICKET_CATEGORIES["complaints"]
    assert "payment_billing" in TICKET_CATEGORIES["business"]
    assert "service_rating" in TICKET_CATEGORIES["feedback"]
    assert ticket_type_definition("payment_billing")["category"] == "business"


def test_ticket_panel_taxonomy_has_unique_type_ids_and_labels():
    from tickets import TICKET_CATEGORIES, ticket_type_definition

    seen = set()
    for category, kinds in TICKET_CATEGORIES.items():
        assert kinds
        for kind, label in kinds.items():
            assert kind not in seen
            assert label
            assert ticket_type_definition(kind)["category"] == category
            seen.add(kind)
    assert len(seen) == sum(len(kinds) for kinds in TICKET_CATEGORIES.values())


def test_expanded_ticket_metadata_is_persisted(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    service = TicketService(db)
    ticket = service.create_ticket(1, 101, 201, "payment_billing", category="business")
    assert ticket.kind == "payment_billing"
    assert ticket.category == "business"
    assert service.get_ticket(ticket.ticket_id).category == "business"


def test_ticket_feedback_accepts_one_rating_and_persists_text(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    service = TicketService(db)
    ticket = service.create_ticket(1, 101, 201, "service_rating", category="feedback")
    service.close_ticket(ticket.ticket_id)
    feedback = service.add_feedback(ticket.ticket_id, 101, 5, "Fast and helpful.")
    assert feedback["rating"] == 5
    assert feedback["comment"] == "Fast and helpful."
    try:
        service.add_feedback(ticket.ticket_id, 101, 4, "Second rating")
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate ticket feedback should be rejected")


def test_ticket_feedback_rejects_invalid_ratings(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    service = TicketService(db)
    ticket = service.create_ticket(1, 101, 201, "general_support", category="support")
    service.close_ticket(ticket.ticket_id)
    for rating in (0, 6):
        try:
            service.add_feedback(ticket.ticket_id, 101, rating, "bad")
        except ValueError:
            pass
        else:
            raise AssertionError("rating outside 1-5 should be rejected")


def test_ticket_ids_are_unique_and_persisted(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    service = TicketService(db)
    first = service.create_ticket(1, 101, 201, "support")
    second = service.create_ticket(1, 102, 202, "support")
    assert first.ticket_id != second.ticket_id
    assert service.get_ticket(first.ticket_id).status == "open"


def test_ticket_overwrites_exclude_everyone_and_allow_opener_and_staff():
    everyone = object()
    opener = object()
    support = object()
    bot_member = object()
    moderator = object()
    overwrites = build_ticket_overwrites(everyone, opener, support, bot_member, staff_roles=[moderator])
    assert overwrites[everyone].view_channel is False
    assert overwrites[opener].view_channel is True
    assert overwrites[support].view_channel is True
    assert overwrites[bot_member].view_channel is True
    assert overwrites[moderator].view_channel is True
    assert overwrites[moderator].send_messages is True


def test_ticket_rooms_category_is_private_and_staff_visible():
    everyone, founder, support = object(), object(), object()
    overwrites = build_ticket_category_overwrites(everyone, [founder, support])
    assert overwrites[everyone].view_channel is False
    for role in (founder, support):
        assert overwrites[role].view_channel is True
        assert overwrites[role].send_messages is True


def test_close_and_reopen_ticket_are_state_transitions(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    service = TicketService(db)
    ticket = service.create_ticket(1, 101, 201, "report")
    assert service.close_ticket(ticket.ticket_id).status == "closed"
    assert service.reopen_ticket(ticket.ticket_id).status == "open"


def test_client_tickets_require_client_or_staff_role(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    service = TicketService(db)
    assert service.can_open(FakeMember(10, "Member"), "client") is False
    assert service.can_open(FakeMember(10, "Client"), "client") is True
    assert service.can_open(FakeMember(10, "Support"), "client") is True
    assert service.can_open(FakeMember(10, "Member"), "support") is True


def test_only_one_open_ticket_per_member_and_kind(tmp_path):
    import sqlite3

    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    service = TicketService(db)
    service.create_ticket(1, 101, 201, "support")
    try:
        service.create_ticket(1, 101, 202, "support")
    except sqlite3.IntegrityError:
        pass
    else:
        raise AssertionError("duplicate open ticket should be rejected")


def test_ticket_category_overwrites_allow_all_staff_roles():
    everyone, founder, moderator, support = object(), object(), object(), object()
    overwrites = build_ticket_category_overwrites(everyone, [founder, moderator, support])
    assert overwrites[everyone].view_channel is False
    assert all(overwrites[role].view_channel is True for role in (founder, moderator, support))
    assert all(overwrites[role].send_messages is True for role in (founder, moderator, support))


def test_ticket_lifecycle_supports_claim_priority_escalation_and_archive_deadline(tmp_path):
    from datetime import timedelta

    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    service = TicketService(db)
    ticket = service.create_ticket(1, 101, 201, "general_support")
    claimed = service.claim_ticket(ticket.ticket_id, 500)
    assert claimed.claimed_by == 500
    prioritized = service.set_priority(ticket.ticket_id, "urgent")
    assert prioritized.priority == "urgent"
    escalated = service.set_escalated(ticket.ticket_id, True)
    assert escalated.escalated is True
    closed = service.close_ticket(ticket.ticket_id, reason="Issue resolved")
    assert closed.status == "closed"
    assert closed.closed_reason == "Issue resolved"
    assert closed.archive_at == closed.closed_at
    assert closed.delete_at is not None
    assert closed.delete_at > closed.closed_at


def test_reopen_cancels_archive_deadline(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    service = TicketService(db)
    ticket = service.create_ticket(1, 101, 201, "general_support")
    service.close_ticket(ticket.ticket_id, reason="Resolved")
    reopened = service.reopen_ticket(ticket.ticket_id)
    assert reopened.status == "open"
    assert reopened.archive_at is None
    assert reopened.closed_at is None


def test_archive_state_is_idempotent_and_never_archives_open_ticket(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    service = TicketService(db)
    ticket = service.create_ticket(1, 101, 201, "general_support")
    assert service.mark_archived(ticket.ticket_id) is False
    service.close_ticket(ticket.ticket_id, reason="Resolved")
    assert service.mark_archived(ticket.ticket_id) is True
    assert service.mark_archived(ticket.ticket_id) is False
    assert service.get_ticket(ticket.ticket_id).status == "archived"


def test_ticket_activity_updates_last_activity(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    service = TicketService(db)
    ticket = service.create_ticket(1, 101, 201, "general_support")
    updated = service.touch_activity(ticket.ticket_id)
    assert updated.last_activity_at is not None
