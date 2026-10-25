from __future__ import annotations

from time import monotonic

from storage import Database

STAFF_ROLES = {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator", "Support"}


def level_for_xp(xp: int) -> int:
    if xp < 0:
        raise ValueError("xp cannot be negative")
    level = 1
    while xp >= 100 * level * (level + 1) // 2:
        level += 1
    return level


class CommunityService:
    def __init__(self, db: Database, *, xp_per_message: int = 15, cooldown_seconds: float = 60.0):
        self.db = db
        self.xp_per_message = xp_per_message
        self.cooldown_seconds = cooldown_seconds

    def _ensure_member(self, member_id: int) -> None:
        self.db.execute("INSERT OR IGNORE INTO members (member_id) VALUES (?)", (member_id,))
        self.db.execute("INSERT OR IGNORE INTO xp (member_id, xp) VALUES (?, 0)", (member_id,))
        self.db.execute("INSERT OR IGNORE INTO member_activity (member_id) VALUES (?)", (member_id,))

    def award_xp(self, member_id: int, amount: int) -> int:
        if amount < 0:
            raise ValueError("amount cannot be negative")
        self._ensure_member(member_id)
        self.db.execute("UPDATE xp SET xp = xp + ?, updated_at=CURRENT_TIMESTAMP WHERE member_id = ?", (amount, member_id))
        return int(self.db.fetchone("SELECT xp FROM xp WHERE member_id = ?", (member_id,))[0])

    def get_profile(self, member_id: int) -> dict[str, int]:
        self._ensure_member(member_id)
        xp = int(self.db.fetchone("SELECT xp FROM xp WHERE member_id = ?", (member_id,))[0])
        return {"member_id": member_id, "xp": xp, "level": level_for_xp(xp)}

    def record_message(self, member_id: int, *, now: float | None = None) -> int:
        self._ensure_member(member_id)
        current = monotonic() if now is None else now
        row = self.db.fetchone("SELECT last_xp_at FROM member_activity WHERE member_id = ?", (member_id,))
        last = row[0]
        if last is not None and current - float(last) < self.cooldown_seconds:
            return 0
        self.db.execute("UPDATE member_activity SET last_xp_at = ? WHERE member_id = ?", (current, member_id))
        self.award_xp(member_id, self.xp_per_message)
        return self.xp_per_message

    def create_suggestion(self, author_id: int, content: str) -> int:
        if not content.strip():
            raise ValueError("suggestion cannot be empty")
        cursor = self.db.execute("INSERT INTO suggestions (author_id, content) VALUES (?, ?)", (author_id, content.strip()))
        return int(cursor.lastrowid)

    def get_suggestion(self, suggestion_id: int):
        return self.db.fetchone("SELECT suggestion_id, author_id, content, created_at FROM suggestions WHERE suggestion_id = ?", (suggestion_id,))

    def can_create_event(self, role_names: set[str]) -> bool:
        return bool(role_names & STAFF_ROLES)

    def create_event(self, creator_id: int, title: str, starts_at: str) -> int:
        if not title.strip() or not starts_at.strip():
            raise ValueError("event title and start time are required")
        cursor = self.db.execute("INSERT INTO community_events (creator_id, title, starts_at) VALUES (?, ?, ?)", (creator_id, title.strip(), starts_at.strip()))
        return int(cursor.lastrowid)

    def get_event(self, event_id: int):
        return self.db.fetchone("SELECT event_id, creator_id, title, starts_at, created_at FROM community_events WHERE event_id = ?", (event_id,))

    def create_reminder(self, member_id: int, message: str, remind_at: str) -> int:
        cursor = self.db.execute("INSERT INTO reminders (member_id, message, remind_at) VALUES (?, ?, ?)", (member_id, message.strip(), remind_at.strip()))
        return int(cursor.lastrowid)
