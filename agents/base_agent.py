from services.ai_service import AIService


class BaseAgent:
    def __init__(
        self,
        name: str,
        responsibility: str,
        system_prompt: str,
        ai_service: AIService,
        keywords: tuple[str, ...],
    ) -> None:
        self.name = name
        self.responsibility = responsibility
        self.system_prompt = system_prompt
        self.ai_service = ai_service
        self.keywords = keywords

    def can_handle(self, user_message: str) -> bool:
        normalized_message = user_message.lower()
        return any(keyword in normalized_message for keyword in self.keywords)

    def run(self, user_message: str, context: str = "") -> str:
        if not self.can_handle(user_message):
            return (
                f"{self.name}: этот вопрос лучше передать другому агенту, "
                "потому что он находится вне моей зоны ответственности."
            )

        message = user_message
        if context:
            message = (
                f"Use these e-commerce store materials when they are relevant:\n"
                f"{context}\n\n"
                f"Customer question:\n{user_message}"
            )

        return self.ai_service.generate_response(self.system_prompt, message)
