from storage import analytics_repository


class AnalyticsService:
    def record_product_matches(
        self,
        products: list[dict],
        query: str,
        user_id: int | None,
        recommended_interaction_type: str = "recommended_by_agent",
    ) -> None:
        for product in products:
            product_db_id = int(product["id"])
            store_id = int(product["store_id"])
            analytics_repository.record_interaction(
                product_db_id,
                store_id,
                user_id,
                query,
                "mentioned_in_query",
            )
            analytics_repository.record_interaction(
                product_db_id,
                store_id,
                user_id,
                query,
                recommended_interaction_type,
            )

    def get_store_analytics(self, store_id: int) -> dict:
        return analytics_repository.get_store_analytics(store_id)
