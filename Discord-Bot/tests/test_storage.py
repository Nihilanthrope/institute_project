import sqlite3

from storage import Database


def test_database_initializes_idempotently(tmp_path):
    path = tmp_path / "rupzha.db"
    db = Database(path)
    db.initialize()
    db.initialize()
    rows = db.fetchall("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('members','xp','moderation_cases','tickets','settings')")
    assert {row[0] for row in rows} == {"members", "xp", "moderation_cases", "tickets", "settings"}


def test_member_xp_persists(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    db.execute("INSERT INTO members (member_id) VALUES (?)", (123,))
    db.execute("INSERT INTO xp (member_id, xp) VALUES (?, ?)", (123, 450))
    assert db.fetchone("SELECT xp FROM xp WHERE member_id = ?", (123,))[0] == 450


def test_ticket_metadata_persists(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    db.execute("INSERT INTO tickets (ticket_id, guild_id, channel_id, opener_id, kind, status) VALUES (?, ?, ?, ?, ?, ?)", ("RZ-0001", 1, 2, 3, "support", "open"))
    row = db.fetchone("SELECT ticket_id, status FROM tickets WHERE ticket_id = ?", ("RZ-0001",))
    assert tuple(row) == ("RZ-0001", "open")


def test_settings_are_upsertable(tmp_path):
    db = Database(tmp_path / "rupzha.db")
    db.initialize()
    db.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", ("guild_id", "1554830636454514708"))
    db.execute("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", ("guild_id", "1554830636454514708"))
    assert db.fetchone("SELECT value FROM settings WHERE key = 'guild_id'")[0] == "1554830636454514708"
