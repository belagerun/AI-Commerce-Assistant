import sqlite3

from config.settings import CHAT_UPLOADS_DIR, DATABASE_PATH, PRODUCT_IMAGES_DIR
from storage.analytics_repository import create_product_interactions_table
from storage.auth_repository import create_users_table
from storage.email_verification_repository import create_email_verification_table
from storage.product_repository import create_products_table
from storage.session_repository import create_user_sessions_table
from storage.store_repository import create_store_profiles_table


def init_database() -> None:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PRODUCT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    CHAT_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                agent_response TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                routing_reason TEXT NOT NULL DEFAULT '',
                user_id INTEGER,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        _add_column_if_missing(
            connection,
            "chat_messages",
            "routing_reason",
            "TEXT NOT NULL DEFAULT ''",
        )
        _add_column_if_missing(connection, "chat_messages", "user_id", "INTEGER")
        _add_column_if_missing(connection, "chat_messages", "session_id", "TEXT")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                agent_scope TEXT NOT NULL,
                content TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(document_id) REFERENCES documents(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                artifact_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    create_users_table()
    create_user_sessions_table()
    create_email_verification_table()
    create_store_profiles_table()
    create_products_table()
    create_product_interactions_table()


def _add_column_if_missing(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_definition: str,
) -> None:
    columns = [
        row[1]
        for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    ]

    if column_name not in columns:
        connection.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        )
