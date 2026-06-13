import sqlite3

from config.settings import DATABASE_PATH


class DatabaseService:
    def save_message(
        self,
        user_message: str,
        agent_response: str,
        agent_name: str,
        routing_reason: str = "",
        user_id: int | None = None,
        session_id: str | None = None,
    ) -> None:
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.execute(
                """
                INSERT INTO chat_messages
                    (user_message, agent_response, agent_name, routing_reason, user_id, session_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_message, agent_response, agent_name, routing_reason, user_id, session_id),
            )

    def get_messages(
        self,
        user_id: int | None = None,
        session_id: str | None = None,
    ) -> list[dict[str, str]]:
        where_clause, params = _chat_scope_clause(user_id, session_id)
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                f"""
                SELECT user_message, agent_response, agent_name, routing_reason, created_at
                FROM chat_messages
                {where_clause}
                ORDER BY id ASC
                """,
                params,
            ).fetchall()

        return [dict(row) for row in rows]

    def clear_messages(
        self,
        user_id: int | None = None,
        session_id: str | None = None,
    ) -> None:
        self.clear_chat_history(user_id=user_id, session_id=session_id)

    def clear_chat_history(
        self,
        user_id: int | None = None,
        session_id: str | None = None,
    ) -> None:
        where_clause, params = _chat_scope_clause(user_id, session_id)
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.execute(f"DELETE FROM chat_messages {where_clause}", params)

    def save_document(self, file_name: str, file_type: str, agent_scope: str, content: str) -> int:
        with sqlite3.connect(DATABASE_PATH) as connection:
            cursor = connection.execute(
                """
                INSERT INTO documents (file_name, file_type, agent_scope, content)
                VALUES (?, ?, ?, ?)
                """,
                (file_name, file_type, agent_scope, content),
            )
            return int(cursor.lastrowid)

    def save_document_chunks(self, document_id: int, chunks: list[str]) -> None:
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.execute("DELETE FROM document_chunks WHERE document_id=?", (document_id,))
            connection.executemany(
                """
                INSERT INTO document_chunks (document_id, chunk_index, chunk_text)
                VALUES (?, ?, ?)
                """,
                [
                    (document_id, chunk_index, chunk_text)
                    for chunk_index, chunk_text in enumerate(chunks, start=1)
                ],
            )

    def get_documents(self) -> list[dict[str, str]]:
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT id, file_name, file_type, agent_scope, uploaded_at
                FROM documents
                ORDER BY id DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def get_chunks_for_agent(self, agent_name: str) -> list[dict[str, str]]:
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT c.chunk_text, c.chunk_index, d.file_name, d.agent_scope
                FROM document_chunks c
                JOIN documents d ON d.id=c.document_id
                WHERE d.agent_scope IN (?, ?)
                ORDER BY d.id DESC, c.chunk_index ASC
                """,
                ("All agents", agent_name),
            ).fetchall()

        return [dict(row) for row in rows]

    def clear_documents(self) -> None:
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.execute("DELETE FROM document_chunks")
            connection.execute("DELETE FROM documents")

    def save_artifact(self, file_name: str, file_path: str, artifact_type: str, file_size: int) -> int:
        with sqlite3.connect(DATABASE_PATH) as connection:
            cursor = connection.execute(
                """
                INSERT INTO artifacts (file_name, file_path, artifact_type, file_size)
                VALUES (?, ?, ?, ?)
                """,
                (file_name, file_path, artifact_type, file_size),
            )
            return int(cursor.lastrowid)

    def get_artifacts(self) -> list[dict[str, str]]:
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT id, file_name, file_path, artifact_type, file_size, created_at
                FROM artifacts
                ORDER BY id DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]


def _chat_scope_clause(
    user_id: int | None = None,
    session_id: str | None = None,
) -> tuple[str, tuple]:
    if user_id is not None:
        return "WHERE user_id=?", (user_id,)
    if session_id:
        return "WHERE session_id=?", (session_id,)
    return "WHERE user_id IS NULL AND session_id IS NULL", ()
