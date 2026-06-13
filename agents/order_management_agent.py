from agents.base_agent import BaseAgent
from config.prompts import ORDER_MANAGEMENT_PROMPT
from services.ai_service import AIService


class OrderManagementAgent(BaseAgent):
    def __init__(self, ai_service: AIService) -> None:
        super().__init__(
            name="Order Management Agent",
            responsibility="Заказы: статус, отмена, возврат, обмен и проблемы с доставкой конкретного заказа.",
            system_prompt=ORDER_MANAGEMENT_PROMPT,
            ai_service=ai_service,
            keywords=(
                "заказ",
                "статус",
                "отмена",
                "отменить",
                "возврат",
                "вернуть",
                "обмен",
                "заменить",
                "номер заказа",
                "трек",
                "посылка",
                "не пришел",
                "не пришла",
                "order",
                "cancel",
                "return",
                "exchange",
                "tracking",
            ),
        )
