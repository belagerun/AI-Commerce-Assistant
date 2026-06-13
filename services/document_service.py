from pathlib import Path
from typing import Any

from config.settings import BASE_DIR
from rag.mini_rag import split_text_into_chunks
from readers.file_reader import read_uploaded_file_with_diagnostics
from services.database_service import DatabaseService


DEMO_MATERIALS = (
    ("delivery_policy.txt", "Customer Support Agent"),
    ("refund_policy.txt", "Order Management Agent"),
    ("product_catalog.txt", "Product Recommendation Agent"),
)


class DocumentService:
    def __init__(self, database_service: DatabaseService) -> None:
        self.database_service = database_service

    def save_uploaded_file(self, uploaded_file, agent_scope: str) -> dict[str, Any]:
        read_result = read_uploaded_file_with_diagnostics(uploaded_file)
        content = read_result["text"]
        if not content.strip():
            diagnostics = read_result.get("diagnostics") or {}
            details = _format_diagnostics(diagnostics)
            raise ValueError(
                "The uploaded file does not contain readable text."
                f"{details}"
            )

        file_type = Path(uploaded_file.name).suffix.lower().lstrip(".") or "txt"
        saved_document = self.save_text_document(uploaded_file.name, file_type, content, agent_scope)
        saved_document["diagnostics"] = read_result.get("diagnostics") or {}
        return saved_document

    def save_text_document(
        self,
        file_name: str,
        file_type: str,
        content: str,
        agent_scope: str,
    ) -> dict[str, Any]:
        if not content.strip():
            raise ValueError("The document does not contain readable text.")

        document_id = self.database_service.save_document(
            file_name,
            file_type,
            agent_scope,
            content,
        )
        chunks = split_text_into_chunks(content)
        self.database_service.save_document_chunks(document_id, chunks)

        return {
            "id": document_id,
            "file_name": file_name,
            "file_type": file_type,
            "chunks_count": len(chunks),
        }

    def load_demo_materials(self) -> list[dict[str, str | int]]:
        loaded_documents = []
        demo_dir = BASE_DIR / "demo_materials"

        for file_name, agent_scope in DEMO_MATERIALS:
            file_path = demo_dir / file_name
            content = file_path.read_text(encoding="utf-8")
            loaded_documents.append(
                self.save_text_document(file_name, "txt", content, agent_scope)
            )

        return loaded_documents

    def get_documents(self) -> list[dict[str, str]]:
        return self.database_service.get_documents()

    def clear_documents(self) -> None:
        self.database_service.clear_documents()


def _format_diagnostics(diagnostics: dict[str, str | int]) -> str:
    if not diagnostics:
        return ""

    return (
        " Diagnostics: "
        f"file={diagnostics.get('file_name', '')}, "
        f"paragraphs={diagnostics.get('paragraph_count', 0)}, "
        f"tables={diagnostics.get('table_count', 0)}, "
        f"characters={diagnostics.get('extracted_character_count', 0)}."
    )
