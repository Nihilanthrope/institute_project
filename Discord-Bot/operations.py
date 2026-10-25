from __future__ import annotations

import re

import discord

from storage import Database

STAFF_ROLES = {"Founder", "Co-Founder", "Administrator", "Operations", "Manager"}
CLIENT_ROLE = "Client"
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)


def sanitize_public_text(text: str) -> str:
    sanitized = URL_RE.sub("[private link removed]", text)
    sanitized = EMAIL_RE.sub("[private email removed]", sanitized)
    return sanitized.strip()


def can_view_project(role_names: set[str]) -> bool:
    return CLIENT_ROLE in role_names or bool(role_names & STAFF_ROLES)


def can_edit_project(role_names: set[str]) -> bool:
    return bool(role_names & STAFF_ROLES)


def set_project_status(db: Database, project_id: str, status: str, summary: str) -> None:
    if not project_id.strip() or not status.strip():
        raise ValueError("project id and status are required")
    db.execute(
        "INSERT INTO projects (project_id, status, summary) VALUES (?, ?, ?) "
        "ON CONFLICT(project_id) DO UPDATE SET status=excluded.status, summary=excluded.summary, updated_at=CURRENT_TIMESTAMP",
        (project_id.strip(), status.strip(), sanitize_public_text(summary)),
    )


def get_project_status(db: Database, project_id: str):
    return db.fetchone("SELECT project_id, status, summary, updated_at FROM projects WHERE project_id = ?", (project_id,))


def create_internal_case(db: Database, creator_id: int, role_names: set[str], note: str) -> int | None:
    if not (role_names & STAFF_ROLES):
        return None
    cursor = db.execute("INSERT INTO internal_cases (creator_id, note) VALUES (?, ?)", (creator_id, note.strip()))
    return int(cursor.lastrowid)


def build_client_status_embed(db: Database, project_id: str, role_names: set[str]):
    if not can_view_project(role_names):
        return None
    row = get_project_status(db, project_id)
    if row is None:
        return discord.Embed(title=f"Project {project_id}", description="No project status is available yet.")
    return discord.Embed(
        title=f"RupZha · Project {row['project_id']}",
        description=f"**Status:** {row['status']}\n\n{row['summary']}",
    )
