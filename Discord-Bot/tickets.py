from __future__ import annotations

from dataclasses import dataclass

import discord

from storage import Database

STAFF_ROLES = {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Support"}
CLIENT_ROLE = "Client"
VALID_KINDS = {"support", "report", "client"}


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    guild_id: int
    channel_id: int
    opener_id: int
    kind: str
    status: str
    created_at: str | None = None
    closed_at: str | None = None


def _ticket_from_row(row) -> Ticket | None:
    return Ticket(**dict(row)) if row else None


def build_ticket_overwrites(everyone, opener, support_role, bot_member):
    return {
        everyone: discord.PermissionOverwrite(view_channel=False),
        opener: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
        support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True),
        bot_member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True, manage_messages=True),
    }


class TicketService:
    def __init__(self, db: Database):
        self.db = db

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
        if kind != "client":
            return True
        role_names = {getattr(role, "name", "") for role in getattr(member, "roles", ())}
        return CLIENT_ROLE in role_names or bool(role_names & STAFF_ROLES)

    def create_ticket(self, guild_id: int, opener_id: int, channel_id: int, kind: str) -> Ticket:
        if kind not in VALID_KINDS:
            raise ValueError(f"invalid ticket kind: {kind}")
        ticket_id = self._next_id()
        self.db.execute(
            "INSERT INTO tickets (ticket_id, guild_id, channel_id, opener_id, kind, status) VALUES (?, ?, ?, ?, ?, 'open')",
            (ticket_id, guild_id, channel_id, opener_id, kind),
        )
        return self.get_ticket(ticket_id)

    def get_ticket(self, ticket_id: str) -> Ticket | None:
        return _ticket_from_row(self.db.fetchone("SELECT ticket_id, guild_id, channel_id, opener_id, kind, status, created_at, closed_at FROM tickets WHERE ticket_id = ?", (ticket_id,)))

    def get_by_channel(self, channel_id: int) -> Ticket | None:
        return _ticket_from_row(self.db.fetchone("SELECT ticket_id, guild_id, channel_id, opener_id, kind, status, created_at, closed_at FROM tickets WHERE channel_id = ? ORDER BY rowid DESC LIMIT 1", (channel_id,)))

    def close_ticket(self, ticket_id: str) -> Ticket:
        if not self.get_ticket(ticket_id):
            raise KeyError(ticket_id)
        self.db.execute("UPDATE tickets SET status='closed', closed_at=CURRENT_TIMESTAMP WHERE ticket_id = ?", (ticket_id,))
        return self.get_ticket(ticket_id)

    def reopen_ticket(self, ticket_id: str) -> Ticket:
        if not self.get_ticket(ticket_id):
            raise KeyError(ticket_id)
        self.db.execute("UPDATE tickets SET status='open', closed_at=NULL WHERE ticket_id = ?", (ticket_id,))
        return self.get_ticket(ticket_id)
