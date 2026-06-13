from agents.base_agent import BaseAgent
from config.prompts import PRODUCT_RECOMMENDATION_PROMPT
from services.ai_service import AIService


class ProductRecommendationAgent(BaseAgent):
    def __init__(self, ai_service: AIService) -> None:
        super().__init__(
            name="Product Recommendation Agent",
            responsibility="Подбор товаров: бюджет, сравнение, характеристики, выбор и анализ отзывов.",
            system_prompt=PRODUCT_RECOMMENDATION_PROMPT,
            ai_service=ai_service,
            keywords=(
                "посоветуй",
                "порекомендуй",
                "выбрать",
                "выбор",
                "подобрать",
                "найди",
                "похожий",
                "похожее",
                "похожие",
                "сравнить",
                "сравни",
                "сравнение",
                "характеристики",
                "бюджет",
                "цена",
                "дешевле",
                "дороже",
                "отзывы",
                "товар",
                "модель",
                "смартфон",
                "смартфона",
                "ноутбук",
                "ноутбука",
                "наушники",
                "наушников",
                "учёбы",
                "учебы",
                "учёба",
                "учеба",
                "recommend",
                "compare",
                "budget",
                "reviews",
                "product",
            ),
        )
