from generators.docx_generator import generate_docx_report
from generators.pptx_generator import generate_pptx_presentation
from services.database_service import DatabaseService


class ArtifactService:
    def __init__(self, database_service: DatabaseService) -> None:
        self.database_service = database_service

    def create_docx_from_history(self, messages: list[dict[str, str]]) -> dict[str, str | int]:
        content = self._messages_to_text(messages)
        sources = self._message_sources(messages)
        artifact = generate_docx_report("E-commerce Customer Service Chat Report", content, sources)
        self._save_artifact(artifact)
        return artifact

    def create_pptx_from_history(self, messages: list[dict[str, str]]) -> dict[str, str | int]:
        content = self._messages_to_text(messages)
        sources = self._message_sources(messages)
        artifact = generate_pptx_presentation("E-commerce Customer Service Brief", content, sources)
        self._save_artifact(artifact)
        return artifact

    def get_artifacts(self) -> list[dict[str, str]]:
        return self.database_service.get_artifacts()

    def _save_artifact(self, artifact: dict[str, str | int]) -> None:
        self.database_service.save_artifact(
            str(artifact["file_name"]),
            str(artifact["file_path"]),
            str(artifact["artifact_type"]),
            int(artifact["file_size"]),
        )

    def _messages_to_text(self, messages: list[dict[str, str]]) -> str:
        if not messages:
            return "No chat messages yet."

        blocks = []
        for message in messages:
            blocks.append(
                f"Customer: {message['user_message']}\n"
                f"Agent: {message['agent_name']}\n"
                f"Answer: {message['agent_response']}"
            )

        return "\n\n".join(blocks)

    def _message_sources(self, messages: list[dict[str, str]]) -> list[str]:
        agents = []
        for message in messages:
            agent_name = message.get("agent_name", "")
            if agent_name and agent_name not in agents:
                agents.append(agent_name)
        return agents
