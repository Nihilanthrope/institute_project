from tickets import TicketService, build_ticket_overwrites
from storage import Database


class FakeRole:
    def __init__(self, name):
        self.name = name


class FakeMember:
    def __init__(self, member_id, *roles):
        self.id = member_id
        self.roles = [FakeRole(name) for name in roles]


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
    overwrites = build_ticket_overwrites(everyone, opener, support, bot_member)
    assert overwrites[everyone].view_channel is False
    assert overwrites[opener].view_channel is True
    assert overwrites[support].view_channel is True
    assert overwrites[bot_member].view_channel is True


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
