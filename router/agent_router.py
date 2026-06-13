from agents.base_agent import BaseAgent


class AgentRouter:
    def __init__(self, agents: list[BaseAgent]) -> None:
        if len(agents) != 3:
            raise ValueError("Router must work with exactly three agents.")
        self.agents = agents

    def route(self, user_message: str, context: str = "") -> tuple[str, str, str]:
        selected_agent, routing_reason = self._select_agent(user_message)
        response = selected_agent.run(user_message, context)
        return selected_agent.name, routing_reason, response

    def select_agent(self, user_message: str) -> tuple[str, str]:
        selected_agent, routing_reason = self._select_agent(user_message)
        return selected_agent.name, routing_reason

    def _select_agent(self, user_message: str) -> tuple[BaseAgent, str]:
        normalized_message = user_message.lower()

        if self._has_order_context(normalized_message):
            return (
                self._get_agent_by_name("Order Management Agent"),
                "Запрос связан с заказом, возвратом, отменой, обменом или доставкой конкретного заказа.",
            )

        if self._has_image_product_context(normalized_message):
            return (
                self._get_agent_by_name("Product Recommendation Agent"),
                "Запрос связан с поиском похожего товара по изображению или подбором продукта.",
            )

        for agent in self.agents:
            if agent.can_handle(user_message):
                return agent, self._reason_for_agent(agent.name)

        return (
            self.agents[0],
            "Запрос не совпал с точными правилами Router, поэтому он передан агенту общей поддержки.",
        )

    def _has_order_context(self, normalized_message: str) -> bool:
        order_terms = (
            "заказ",
            "номер заказа",
            "статус",
            "отмена",
            "отменить",
            "возврат",
            "вернуть",
            "обмен",
            "трек",
            "посылка",
            "order",
            "cancel",
            "return",
            "exchange",
            "tracking",
        )
        return any(term in normalized_message for term in order_terms)

    def _has_image_product_context(self, normalized_message: str) -> bool:
        image_product_terms = (
            "похож",
            "похожий товар",
            "похожее",
            "найди похожий",
            "хочу купить похожее",
            "uploaded image",
            "similar product",
            "something like this",
            "find similar",
            "image search",
        )
        return any(term in normalized_message for term in image_product_terms)

    def _get_agent_by_name(self, agent_name: str) -> BaseAgent:
        for agent in self.agents:
            if agent.name == agent_name:
                return agent
        raise ValueError(f"Agent not found: {agent_name}")

    def _reason_for_agent(self, agent_name: str) -> str:
        reasons = {
            "Customer Support Agent": "Запрос связан с доставкой, оплатой, FAQ, графиком или общими правилами магазина.",
            "Order Management Agent": "Запрос связан с управлением заказом: статусом, отменой, возвратом или обменом.",
            "Product Recommendation Agent": "Запрос связан с подбором, сравнением, характеристиками, ценой или отзывами о товарах.",
        }
        return reasons.get(agent_name, "Router выбрал наиболее подходящего агента по содержанию запроса.")
