import sqlite3

from config.settings import DATABASE_PATH


def delete_user_account(user_id: int) -> dict:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("BEGIN")
            user = connection.execute(
                """
                SELECT id, email, account_type
                FROM users
                WHERE id=?
                LIMIT 1
                """,
                (user_id,),
            ).fetchone()
            if user is None:
                raise ValueError("User account was not found.")

            deleted = {
                "account_type": user["account_type"],
                "store_id": None,
            }

            store = connection.execute(
                """
                SELECT id
                FROM store_profiles
                WHERE user_id=?
                LIMIT 1
                """,
                (user_id,),
            ).fetchone()

            if user["account_type"] == "store" and store is not None:
                store_id = int(store["id"])
                deleted["store_id"] = store_id
                delete_store_analytics(connection, store_id)
                delete_store_products(connection, store_id)
                delete_store_profile(connection, user_id)

            delete_user_sessions(connection, user_id)
            delete_user_chat_history(connection, user_id)
            delete_user_product_interactions(connection, user_id)
            delete_email_verification_records(connection, user["email"])
            connection.execute("DELETE FROM users WHERE id=?", (user_id,))
            connection.commit()
            return deleted
        except Exception:
            connection.rollback()
            raise


def delete_user_sessions(connection: sqlite3.Connection, user_id: int) -> None:
    connection.execute("DELETE FROM user_sessions WHERE user_id=?", (user_id,))


def delete_user_chat_history(connection: sqlite3.Connection, user_id: int) -> None:
    connection.execute("DELETE FROM chat_messages WHERE user_id=?", (user_id,))


def delete_user_product_interactions(connection: sqlite3.Connection, user_id: int) -> None:
    connection.execute("DELETE FROM product_interactions WHERE user_id=?", (user_id,))


def delete_email_verification_records(connection: sqlite3.Connection, email: str) -> None:
    connection.execute("DELETE FROM email_verification_codes WHERE email=?", (email,))


def delete_store_profile(connection: sqlite3.Connection, user_id: int) -> None:
    connection.execute("DELETE FROM store_profiles WHERE user_id=?", (user_id,))


def delete_store_products(connection: sqlite3.Connection, store_id: int) -> None:
    connection.execute("DELETE FROM products WHERE store_id=?", (store_id,))


def delete_store_analytics(connection: sqlite3.Connection, store_id: int) -> None:
    connection.execute("DELETE FROM product_interactions WHERE store_id=?", (store_id,))
