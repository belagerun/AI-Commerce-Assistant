import sqlite3

from config.settings import DATABASE_PATH


def create_user_sessions_table() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                revoked INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_user_sessions_token_hash
            ON user_sessions(token_hash)
            """
        )


def insert_session(
    user_id: int,
    token_hash: str,
    created_at: str,
    expires_at: str,
) -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT INTO user_sessions (user_id, token_hash, created_at, expires_at, revoked)
            VALUES (?, ?, ?, ?, 0)
            """,
            (user_id, token_hash, created_at, expires_at),
        )


def find_valid_session(token_hash: str, now: str) -> dict | None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT
                s.id AS session_id,
                s.user_id,
                s.token_hash,
                s.created_at,
                s.expires_at,
                s.revoked,
                u.id,
                u.username,
                u.email,
                u.account_type
            FROM user_sessions s
            JOIN users u ON u.id=s.user_id
            WHERE s.token_hash=?
              AND s.revoked=0
              AND s.expires_at>?
            LIMIT 1
            """,
            (token_hash, now),
        ).fetchone()

    return dict(row) if row else None


def revoke_session(token_hash: str) -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            UPDATE user_sessions
            SET revoked=1
            WHERE token_hash=?
            """,
            (token_hash,),
        )


def cleanup_expired_sessions(now: str) -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            UPDATE user_sessions
            SET revoked=1
            WHERE expires_at<=? AND revoked=0
            """,
            (now,),
        )
