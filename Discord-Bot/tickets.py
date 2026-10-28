from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import discord

from storage import Database

STAFF_ROLES = {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator", "Support"}
CLIENT_ROLE = "Client"

TICKET_CATEGORIES = {
    "support": {
        "general_support": "General Support",
        "question_help": "Question / Help",
        "other_contact": "Other / Contact Staff",
        "account_role": "Account / Role Problem",
        "ticket_problem": "Ticket Problem",
        "message_channel": "Message / Channel Issue",
        "bot_problem": "Bot Problem",
        "bug_report": "Bug Report",
    },
    "complaints": {
        "complaint": "Complaint",
        "member_report": "Report a Member",
        "security_privacy": "Security / Privacy Issue",
        "moderation_appeal": "Moderation Appeal",
        "punishment_appeal": "Punishment Appeal",
        "negative_feedback": "Negative Feedback / Complaint",
    },
    "business": {
        "service_inquiry": "Service Inquiry",
        "partnership": "Partnership",
        "payment_billing": "Payment / Billing",
        "order_purchase": "Order / Purchase Issue",
        "project_support": "Project Support",
        "refund_cancellation": "Refund / Cancellation",
        "project_feedback": "Project Feedback",
    },
    "feedback": {
        "service_rating": "Rate Our Service",
        "general_feedback": "Give Feedback",
        "suggestion": "Suggestion / Feature Request",
        "appreciation": "Appreciation / Positive Feedback",
    },
}

LEGACY_KIND_CATEGORIES = {"support": "support", "report": "complaints", "client": "business"}
VALID_KINDS = set(LEGACY_KIND_CATEGORIES) | {kind for kinds in TICKET_CATEGORIES.values() for kind in kinds}
CLIENT_KINDS = set(TICKET_CATEGORIES["business"]) | {"client"}


def ticket_type_definition(kind: str) -> dict:
    if kind in LEGACY_KIND_CATEGORIES:
        category = LEGACY_KIND_CATEGORIES[kind]
        return {"kind": kind, "category": category, "label": kind.title()}
    for category, kinds in TICKET_CATEGORIES.items():
        if kind in kinds:
            return {"kind": kind, "category": category, "label": kinds[kind]}
    raise ValueError(f"invalid ticket kind: {kind}")


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    guild_id: int
    channel_id: int
    opener_id: int
    kind: str
    status: str
    category: str = "support"
    created_at: str | None = None
    closed_at: str | None = None
    closed_reason: str = ""
    claimed_by: int | None = None
    priority: str = "normal"
    escalated: bool = False
    last_activity_at: str | None = None
    archive_at: str | None = None
    delete_at: str | None = None
    transcript_path: str | None = None


def _ticket_from_row(row) -> Ticket | None:
    if not row:
        return None
    data = dict(row)
    data["escalated"] = bool(data.get("escalated", 0))
    return Ticket(**data)


def build_ticket_category_overwrites(everyone, staff_roles):
    overwrites = {everyone: discord.PermissionOverwrite(view_channel=False)}
    for role in staff_roles:
        overwrites[role] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
        )
    return overwrites


def build_ticket_overwrites(everyone, opener, support_role, bot_member, *, staff_roles=()):
    overwrites = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        opener: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
        support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True),
        bot_member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True, manage_messages=True),
    }
    for role in staff_roles:
        if role in (everyone, support_role):
            continue
        overwrites[role] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            manage_messages=True,
        )
    return overwrites


class TicketService:
    ARCHIVE_DELAY_HOURS = 24
    VALID_PRIORITIES = {"low", "normal", "high", "urgent"}

    def __init__(self, db: Database):
        self.db = db

    @staticmethod
    def _select_columns() -> str:
        return ("ticket_id, guild_id, channel_id, opener_id, kind, status, category, "
                "created_at, closed_at, closed_reason, claimed_by, priority, escalated, "
                "last_activity_at, archive_at, delete_at, transcript_path")

    def _next_id(self) -> str:
        row = self.db.fetchone("SELECT ticket_id FROM tickets ORDER BY rowid DESC LIMIT 1")
        if not row:
            return "RZ-0001"
        try:
            number = int(str(row[0]).split("-")[-1]) + 1
        except (ValueError, AttributeError):
            number = self.db.fetchone("SELECT COUNT(*) + 1 FROM tickets")[0]
        return f"RZ-{number:04d}"

    def can_open(self, member, kind: str) -> bool:
        if kind not in VALID_KINDS:
            return False
        if kind not in CLIENT_KINDS:
            return True
        role_names = {getattr(role, "name", "") for role in getattr(member, "roles", ())}
        return CLIENT_ROLE in role_names or bool(role_names & STAFF_ROLES)

    def create_ticket(self, guild_id: int, opener_id: int, channel_id: int, kind: str, *, category: str | None = None) -> Ticket:
        definition = ticket_type_definition(kind)
        category = category or definition["category"]
        if category != definition["category"]:
            raise ValueError(f"ticket kind {kind} does not belong to category {category}")
        ticket_id = self._next_id()
        self.db.execute(
            "INSERT INTO tickets (ticket_id, guild_id, channel_id, opener_id, kind, category, status) VALUES (?, ?, ?, ?, ?, ?, 'open')",
            (ticket_id, guild_id, channel_id, opener_id, kind, category),
        )
        return self.get_ticket(ticket_id)

    def get_ticket(self, ticket_id: str) -> Ticket | None:
        return _ticket_from_row(self.db.fetchone(f"SELECT {self._select_columns()} FROM tickets WHERE ticket_id = ?", (ticket_id,)))

    def get_by_channel(self, channel_id: int) -> Ticket | None:
        return _ticket_from_row(self.db.fetchone(f"SELECT {self._select_columns()} FROM tickets WHERE channel_id = ? ORDER BY rowid DESC LIMIT 1", (channel_id,)))

    def claim_ticket(self, ticket_id: str, member_id: int) -> Ticket:
        if not self.get_ticket(ticket_id):
            raise KeyError(ticket_id)
        self.db.execute("UPDATE tickets SET claimed_by = ?, last_activity_at = CURRENT_TIMESTAMP WHERE ticket_id = ? AND status = 'open'", (member_id, ticket_id))
        return self.get_ticket(ticket_id)

    def unclaim_ticket(self, ticket_id: str) -> Ticket:
        if not self.get_ticket(ticket_id):
            raise KeyError(ticket_id)
        self.db.execute("UPDATE tickets SET claimed_by = NULL, last_activity_at = CURRENT_TIMESTAMP WHERE ticket_id = ? AND status = 'open'", (ticket_id,))
        return self.get_ticket(ticket_id)

    def set_priority(self, ticket_id: str, priority: str) -> Ticket:
        if priority not in self.VALID_PRIORITIES:
            raise ValueError("invalid ticket priority")
        if not self.get_ticket(ticket_id):
            raise KeyError(ticket_id)
        self.db.execute("UPDATE tickets SET priority = ?, last_activity_at = CURRENT_TIMESTAMP WHERE ticket_id = ?", (priority, ticket_id))
        return self.get_ticket(ticket_id)

    def set_escalated(self, ticket_id: str, escalated: bool = True) -> Ticket:
        if not self.get_ticket(ticket_id):
            raise KeyError(ticket_id)
        self.db.execute("UPDATE tickets SET escalated = ?, last_activity_at = CURRENT_TIMESTAMP WHERE ticket_id = ?", (int(escalated), ticket_id))
        return self.get_ticket(ticket_id)

    def touch_activity(self, ticket_id: str) -> Ticket:
        if not self.get_ticket(ticket_id):
            raise KeyError(ticket_id)
        self.db.execute("UPDATE tickets SET last_activity_at = CURRENT_TIMESTAMP WHERE ticket_id = ? AND status = 'open'", (ticket_id,))
        return self.get_ticket(ticket_id)

    def close_ticket(self, ticket_id: str, reason: str = "") -> Ticket:
        if not self.get_ticket(ticket_id):
            raise KeyError(ticket_id)
        reason = (reason or "Resolved").strip()[:500]
        self.db.execute(
            "UPDATE tickets SET status='closed', closed_at=CURRENT_TIMESTAMP, closed_reason=?, archive_at=CURRENT_TIMESTAMP, delete_at=datetime(CURRENT_TIMESTAMP, '+24 hours') WHERE ticket_id = ? AND status='open'",
            (reason, ticket_id),
        )
        return self.get_ticket(ticket_id)

    def reopen_ticket(self, ticket_id: str) -> Ticket:
        if not self.get_ticket(ticket_id):
            raise KeyError(ticket_id)
        self.db.execute("UPDATE tickets SET status='open', closed_at=NULL, closed_reason='', archive_at=NULL, delete_at=NULL, transcript_path=NULL, last_activity_at=CURRENT_TIMESTAMP WHERE ticket_id = ? AND status IN ('closed', 'archived')", (ticket_id,))
        return self.get_ticket(ticket_id)

    def mark_archived(self, ticket_id: str) -> bool:
        ticket = self.get_ticket(ticket_id)
        if ticket is None or ticket.status != 'closed':
            return False
        self.db.execute("UPDATE tickets SET status='archived' WHERE ticket_id = ? AND status='closed'", (ticket_id,))
        return True

    def set_transcript_path(self, ticket_id: str, path: str) -> Ticket:
        self.db.execute("UPDATE tickets SET transcript_path = ? WHERE ticket_id = ?", (path, ticket_id))
        return self.get_ticket(ticket_id)

    def due_archival_tickets(self) -> list[Ticket]:
        rows = self.db.fetchall(f"SELECT {self._select_columns()} FROM tickets WHERE status='closed' AND archive_at IS NOT NULL AND archive_at <= CURRENT_TIMESTAMP")
        return [_ticket_from_row(row) for row in rows]

    def add_feedback(self, ticket_id: str, member_id: int, rating: int, comment: str = "") -> dict:
        ticket = self.get_ticket(ticket_id)
        if ticket is None:
            raise KeyError(ticket_id)
        if ticket.status not in {"closed", "archived"}:
            raise ValueError("ticket must be closed before feedback can be submitted")
        if member_id != ticket.opener_id:
            raise PermissionError("only the ticket opener can submit feedback")
        if rating not in range(1, 6):
            raise ValueError("rating must be between 1 and 5")
        existing = self.db.fetchone("SELECT feedback_id FROM ticket_feedback WHERE ticket_id = ?", (ticket_id,))
        if existing:
            raise ValueError("ticket feedback already exists")
        comment = (comment or "").strip()[:2000]
        cursor = self.db.execute(
            "INSERT INTO ticket_feedback (ticket_id, member_id, rating, comment) VALUES (?, ?, ?, ?)",
            (ticket_id, member_id, rating, comment),
        )
        row = self.db.fetchone(
            "SELECT feedback_id, ticket_id, member_id, rating, comment, created_at FROM ticket_feedback WHERE feedback_id = ?",
            (cursor.lastrowid,),
        )
        return dict(row)
