from agents.base_agent import BaseAgent
from config.prompts import CUSTOMER_SUPPORT_PROMPT
from services.ai_service import AIService


class CustomerSupportAgent(BaseAgent):
    def __init__(self, ai_service: AIService) -> None:
        super().__init__(
            name="Customer Support Agent",
            responsibility="Общие вопросы клиентов: доставка, оплата, график, поддержка и правила магазина.",
            system_prompt=CUSTOMER_SUPPORT_PROMPT,
            ai_service=ai_service,
            keywords=(
                "доставка",
                "доставки",
                "доставку",
                "оплата",
                "оплаты",
                "оплату",
                "платеж",
                "карта",
                "наличные",
                "график",
                "работаете",
                "часы",
                "поддержка",
                "правила",
                "магазин",
                "shipping",
                "payment",
                "working hours",
                "support",
                "policy",
            ),
        )
