import sqlite3

from config.settings import DATABASE_PATH


def create_store_profiles_table() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS store_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                store_name TEXT NOT NULL,
                description TEXT,
                website_url TEXT,
                address TEXT,
                gps_2gis_url TEXT,
                gps_yandex_url TEXT,
                gps_google_url TEXT,
                gps_map_url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        _add_column_if_missing(connection, "store_profiles", "gps_map_url", "TEXT")


def get_store_profile_by_user_id(user_id: int) -> dict | None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT id, user_id, store_name, description, website_url, address,
                   gps_2gis_url, gps_yandex_url, gps_google_url,
                   COALESCE(NULLIF(gps_map_url, ''), NULLIF(gps_2gis_url, ''),
                            NULLIF(gps_yandex_url, ''), NULLIF(gps_google_url, ''), '') AS gps_map_url,
                   created_at
            FROM store_profiles
            WHERE user_id=?
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()

    return dict(row) if row else None


def get_store_profile_by_id(store_id: int) -> dict | None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT id, user_id, store_name, description, website_url, address,
                   gps_2gis_url, gps_yandex_url, gps_google_url,
                   COALESCE(NULLIF(gps_map_url, ''), NULLIF(gps_2gis_url, ''),
                            NULLIF(gps_yandex_url, ''), NULLIF(gps_google_url, ''), '') AS gps_map_url,
                   created_at
            FROM store_profiles
            WHERE id=?
            LIMIT 1
            """,
            (store_id,),
        ).fetchone()

    return dict(row) if row else None


def upsert_store_profile(
    user_id: int,
    store_name: str,
    description: str,
    website_url: str,
    address: str,
    gps_map_url: str,
) -> int:
    existing = get_store_profile_by_user_id(user_id)
    with sqlite3.connect(DATABASE_PATH) as connection:
        if existing:
            connection.execute(
                """
                UPDATE store_profiles
                SET store_name=?, description=?, website_url=?, address=?,
                    gps_map_url=?
                WHERE user_id=?
                """,
                (
                    store_name,
                    description,
                    website_url,
                    address,
                    gps_map_url,
                    user_id,
                ),
            )
            return int(existing["id"])

        cursor = connection.execute(
            """
            INSERT INTO store_profiles
                (user_id, store_name, description, website_url, address, gps_map_url)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                store_name,
                description,
                website_url,
                address,
                gps_map_url,
            ),
        )
        return int(cursor.lastrowid)


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
