import re
import sqlite3

from config.settings import DATABASE_PATH


def create_products_table() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_id INTEGER NOT NULL DEFAULT 1,
                product_id TEXT NOT NULL,
                name TEXT NOT NULL,
                barcode TEXT,
                price REAL NOT NULL,
                description TEXT,
                image_path TEXT,
                image_description TEXT,
                image_url TEXT,
                category TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(store_id, product_id)
            )
            """
        )
        _add_column_if_missing(connection, "products", "store_id", "INTEGER NOT NULL DEFAULT 1")
        _add_column_if_missing(connection, "products", "created_at", "TEXT DEFAULT CURRENT_TIMESTAMP")
        _add_column_if_missing(connection, "products", "image_path", "TEXT")
        _add_column_if_missing(connection, "products", "image_description", "TEXT")
        _add_column_if_missing(connection, "products", "image_url", "TEXT")
        _add_column_if_missing(connection, "products", "category", "TEXT")


def add_product(
    store_id: int,
    product_id: str,
    name: str,
    barcode: str,
    price: float,
    description: str,
    image_path: str = "",
    image_description: str = "",
    image_url: str = "",
    category: str = "",
) -> int:
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.execute(
            """
            INSERT INTO products
                (store_id, product_id, name, barcode, price, description,
                 image_path, image_description, image_url, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                store_id,
                product_id,
                name,
                barcode or None,
                price,
                description,
                image_path or None,
                image_description or None,
                image_url or None,
                category or None,
            ),
        )
        return int(cursor.lastrowid)


def get_all_products(store_id: int | None = None) -> list[dict[str, str | float | int]]:
    where = ""
    params = ()
    if store_id is not None:
        where = "WHERE p.store_id=?"
        params = (store_id,)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            f"""
            SELECT p.id, p.store_id, p.product_id, p.name, p.barcode, p.price, p.description,
                   p.image_path, p.image_description, p.image_url, p.category,
                   s.store_name, s.website_url, s.address,
                   COALESCE(NULLIF(s.gps_map_url, ''), NULLIF(s.gps_2gis_url, ''),
                            NULLIF(s.gps_yandex_url, ''), NULLIF(s.gps_google_url, ''), '') AS gps_map_url
            FROM products
            p LEFT JOIN store_profiles s ON s.id=p.store_id
            {where}
            ORDER BY p.name ASC
            """,
            params,
        ).fetchall()

    return [dict(row) for row in rows]


def get_product_by_id(product_id: str, store_id: int | None = None) -> dict[str, str | float | int] | None:
    where = "WHERE p.product_id=?"
    params: list[str | int] = [product_id]
    if store_id is not None:
        where += " AND p.store_id=?"
        params.append(store_id)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            f"""
            SELECT p.id, p.store_id, p.product_id, p.name, p.barcode, p.price, p.description,
                   p.image_path, p.image_description, p.image_url, p.category,
                   s.store_name, s.website_url, s.address,
                   COALESCE(NULLIF(s.gps_map_url, ''), NULLIF(s.gps_2gis_url, ''),
                            NULLIF(s.gps_yandex_url, ''), NULLIF(s.gps_google_url, ''), '') AS gps_map_url
            FROM products p
            LEFT JOIN store_profiles s ON s.id=p.store_id
            {where}
            LIMIT 1
            """,
            params,
        ).fetchone()

    return dict(row) if row else None


def search_products(query: str, store_id: int | None = None) -> list[dict[str, str | float | int]]:
    terms = _query_terms(query)
    if not terms:
        return get_all_products(store_id)

    search_parts = []
    params = []

    for term in terms:
        like_term = f"%{term}%"
        search_parts.append(
            """
            (
                LOWER(p.product_id) LIKE ?
                OR LOWER(p.name) LIKE ?
                OR LOWER(COALESCE(p.barcode, '')) LIKE ?
                OR LOWER(COALESCE(p.description, '')) LIKE ?
                OR LOWER(COALESCE(p.image_description, '')) LIKE ?
                OR LOWER(COALESCE(p.category, '')) LIKE ?
            )
            """
        )
        params.extend([like_term, like_term, like_term, like_term, like_term, like_term])

    where_clause = f"({' OR '.join(search_parts)})"
    if store_id is not None:
        where_clause = f"p.store_id=? AND {where_clause}"
        params.insert(0, store_id)

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            f"""
            SELECT p.id, p.store_id, p.product_id, p.name, p.barcode, p.price, p.description,
                   p.image_path, p.image_description, p.image_url, p.category,
                   s.store_name, s.website_url, s.address,
                   COALESCE(NULLIF(s.gps_map_url, ''), NULLIF(s.gps_2gis_url, ''),
                            NULLIF(s.gps_yandex_url, ''), NULLIF(s.gps_google_url, ''), '') AS gps_map_url
            FROM products p
            LEFT JOIN store_profiles s ON s.id=p.store_id
            WHERE {where_clause}
            ORDER BY p.price ASC, p.name ASC
            """,
            params,
        ).fetchall()

    return [dict(row) for row in rows]


def update_product(
    store_id: int,
    product_id: str,
    name: str,
    barcode: str,
    price: float,
    description: str,
    image_path: str | None = None,
    image_description: str | None = None,
    image_url: str | None = None,
    category: str | None = None,
) -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            UPDATE products
            SET name=?, barcode=?, price=?, description=?,
                image_path=?, image_description=?, image_url=?, category=?
            WHERE store_id=? AND product_id=?
            """,
            (
                name,
                barcode or None,
                price,
                description,
                image_path or None,
                image_description or None,
                image_url or None,
                category or None,
                store_id,
                product_id,
            ),
        )


def delete_product(product_id: str, store_id: int | None = None) -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        if store_id is None:
            connection.execute("DELETE FROM products WHERE product_id=?", (product_id,))
        else:
            connection.execute(
                "DELETE FROM products WHERE store_id=? AND product_id=?",
                (store_id, product_id),
            )


def _query_terms(query: str) -> list[str]:
    return [
        term
        for term in re.findall(r"[\wа-яА-ЯёЁ]+", (query or "").lower())
        if len(term) > 2
    ]


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
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")
