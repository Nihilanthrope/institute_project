from __future__ import annotations

from collections import deque
from time import monotonic
from typing import Any

from storage import Database

DEFAULT_STAFF_ROLES = {"Founder", "Co-Founder", "Administrator", "Operations", "Manager", "Moderator", "Support"}
DEFAULT_SECURITY_LOG_CHANNEL = "・𝗦𝗲𝗰𝘂𝗿𝗶𝘁𝘆・𝗟𝗼𝗴𝘀"


def is_staff(member: Any, staff_roles: set[str] | None = None) -> bool:
    allowed = staff_roles or DEFAULT_STAFF_ROLES
    return any(getattr(role, "name", None) in allowed for role in getattr(member, "roles", ()))


def can_moderate(actor: Any, target: Any) -> bool:
    if actor is target:
        return False
    actor_top = getattr(getattr(actor, "top_role", None), "position", -1)
    target_top = getattr(getattr(target, "top_role", None), "position", -1)
    return target_top < actor_top


def record_case(db: Database, guild_id: int, target_id: int, actor_id: int, action: str, reason: str) -> int:
    cursor = db.execute(
        "INSERT INTO moderation_cases (guild_id, target_id, actor_id, action, reason) VALUES (?, ?, ?, ?, ?)",
        (guild_id, target_id, actor_id, action, reason),
    )
    return int(cursor.lastrowid)


def get_recent_cases(db: Database, guild_id: int, target_id: int, limit: int = 25) -> list[Any]:
    return db.fetchall(
        "SELECT case_id, guild_id, target_id, actor_id, action, reason, created_at "
        "FROM moderation_cases WHERE guild_id = ? AND target_id = ? "
        "ORDER BY case_id DESC LIMIT ?",
        (guild_id, target_id, limit),
    )


def security_log_channel_name(settings: dict[str, str] | None = None) -> str:
    return (settings or {}).get("security_log_channel", DEFAULT_SECURITY_LOG_CHANNEL)


async def log_security_event(channel: Any, title: str, description: str, *, color: Any = None) -> Any:
    import discord

    embed = discord.Embed(title=title, description=description, color=color)
    return await channel.send(embed=embed)


class JoinGuard:
    def __init__(self, window_seconds: float = 10.0, threshold: int = 8):
        self.window_seconds = window_seconds
        self.threshold = threshold
        self._joins: deque[tuple[float, int]] = deque()

    def record(self, member_id: int, *, now: float | None = None) -> list[int]:
        current = monotonic() if now is None else now
        cutoff = current - self.window_seconds
        while self._joins and self._joins[0][0] < cutoff:
            self._joins.popleft()
        self._joins.append((current, member_id))
        if len(self._joins) < self.threshold:
            return []
        return [member_id for _, member_id in self._joins]
