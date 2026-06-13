from router.agent_router import AgentRouter
from rag.mini_rag import format_context, search_relevant_chunks
from services.analytics_service import AnalyticsService
from services.ai_service import AIService
from services.database_service import DatabaseService
from services.product_service import ProductService


class ChatService:
    def __init__(
        self,
        router: AgentRouter,
        database_service: DatabaseService,
        product_service: ProductService | None = None,
        analytics_service: AnalyticsService | None = None,
        ai_service: AIService | None = None,
    ) -> None:
        self.router = router
        self.database_service = database_service
        self.product_service = product_service
        self.analytics_service = analytics_service
        self.ai_service = ai_service

    def handle_message(
        self,
        user_message: str,
        user_id: int | None = None,
        session_id: str | None = None,
        image_path: str | None = None,
    ) -> tuple[str, str, str]:
        effective_message = _message_with_image_signal(user_message, image_path)
        selected_agent_name, _ = self.router.select_agent(effective_message)
        context = self._find_context(effective_message, selected_agent_name, user_id, image_path)
        agent_name, routing_reason, agent_response = self.router.route(effective_message, context)
        self.database_service.save_message(
            effective_message,
            agent_response,
            agent_name,
            routing_reason,
            user_id,
            session_id,
        )
        return agent_name, routing_reason, agent_response

    def get_history(
        self,
        user_id: int | None = None,
        session_id: str | None = None,
    ) -> list[dict[str, str]]:
        return self.database_service.get_messages(user_id=user_id, session_id=session_id)

    def clear_history(
        self,
        user_id: int | None = None,
        session_id: str | None = None,
    ) -> None:
        self.database_service.clear_chat_history(user_id=user_id, session_id=session_id)

    def _find_context(
        self,
        user_message: str,
        agent_name: str,
        user_id: int | None = None,
        image_path: str | None = None,
    ) -> str:
        chunks = self.database_service.get_chunks_for_agent(agent_name)
        relevant_chunks = search_relevant_chunks(user_message, chunks)
        document_context = format_context(relevant_chunks)

        if agent_name != "Product Recommendation Agent" or self.product_service is None:
            return document_context

        image_context = ""
        search_query = user_message
        image_search = bool(image_path)
        if image_path:
            image_description = self.ai_service.describe_image(image_path) if self.ai_service else ""
            if image_description:
                image_context = (
                    "Uploaded image context:\n"
                    f"Image path: {image_path}\n"
                    f"Vision description: {image_description}\n"
                    "If products match this description, mention that they matched the uploaded image."
                )
                search_query = f"{user_message}\n{image_description}"
            else:
                image_context = (
                    "Uploaded image context:\n"
                    f"Image path: {image_path}\n"
                    "User uploaded an image, but image analysis is not available. "
                    "Ask the user to describe the product or use text search if no clear product match is found."
                )

        products = self.product_service.search_products(search_query)[:5]
        if self.analytics_service is not None:
            self.analytics_service.record_product_matches(
                products,
                user_message or "image search",
                user_id,
                "image_search_recommended" if image_search else "recommended_by_agent",
            )
        product_context = self.product_service.format_product_list_for_agent(products)
        return "\n\n".join(
            context
            for context in (document_context, image_context, product_context)
            if context
        )


def _message_with_image_signal(user_message: str, image_path: str | None) -> str:
    if not image_path:
        return user_message
    if user_message.strip():
        return f"{user_message}\n\n[User uploaded an image for similar product search.]"
    return "Find similar products based on this image.\n\n[User uploaded an image for similar product search.]"
