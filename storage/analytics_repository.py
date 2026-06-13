import sqlite3

from config.settings import DATABASE_PATH


def create_product_interactions_table() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS product_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_db_id INTEGER,
                store_id INTEGER,
                user_id INTEGER NULL,
                query TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def record_interaction(
    product_db_id: int | None,
    store_id: int | None,
    user_id: int | None,
    query: str,
    interaction_type: str,
) -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT INTO product_interactions
                (product_db_id, store_id, user_id, query, interaction_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (product_db_id, store_id, user_id, query, interaction_type),
        )


def get_store_analytics(store_id: int) -> dict:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        total = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM product_interactions
            WHERE store_id=?
            """,
            (store_id,),
        ).fetchone()["total"]

        top_mentioned = connection.execute(
            """
            SELECT p.name, COUNT(*) AS count
            FROM product_interactions i
            JOIN products p ON p.id=i.product_db_id
            WHERE i.store_id=? AND i.interaction_type='mentioned_in_query'
            GROUP BY p.id, p.name
            ORDER BY count DESC
            LIMIT 10
            """,
            (store_id,),
        ).fetchall()

        top_recommended = connection.execute(
            """
            SELECT p.name, COUNT(*) AS count
            FROM product_interactions i
            JOIN products p ON p.id=i.product_db_id
            WHERE i.store_id=? AND i.interaction_type IN ('recommended_by_agent', 'image_search_recommended')
            GROUP BY p.id, p.name
            ORDER BY count DESC
            LIMIT 10
            """,
            (store_id,),
        ).fetchall()

        recent_queries = connection.execute(
            """
            SELECT query, interaction_type, created_at
            FROM product_interactions
            WHERE store_id=?
            ORDER BY id DESC
            LIMIT 20
            """,
            (store_id,),
        ).fetchall()

    return {
        "total": total,
        "top_mentioned": [dict(row) for row in top_mentioned],
        "top_recommended": [dict(row) for row in top_recommended],
        "recent_queries": [dict(row) for row in recent_queries],
    }
