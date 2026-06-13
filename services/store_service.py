from storage import store_repository


class StoreService:
    def get_profile(self, user_id: int) -> dict | None:
        return store_repository.get_store_profile_by_user_id(user_id)

    def save_profile(
        self,
        user_id: int,
        store_name: str,
        description: str,
        website_url: str,
        address: str,
        gps_map_url: str,
    ) -> int:
        if not store_name.strip():
            raise ValueError("Store name is required.")

        return store_repository.upsert_store_profile(
            user_id,
            store_name.strip(),
            description.strip(),
            website_url.strip(),
            address.strip(),
            gps_map_url.strip(),
        )
