import re

from services.analytics_service import AnalyticsService
from services.product_service import ProductService
from services.store_service import StoreService


class StoreAssistantService:
    def __init__(
        self,
        store_service: StoreService,
        product_service: ProductService,
        analytics_service: AnalyticsService,
    ) -> None:
        self.store_service = store_service
        self.product_service = product_service
        self.analytics_service = analytics_service

    def handle_command(
        self,
        command: str,
        current_user: dict,
        store_profile: dict,
    ) -> dict:
        command = command.strip()
        if not command:
            return _message("Please enter a store assistant command.")

        store_id = int(store_profile["id"])

        price_intent = self._parse_price_update(command)
        if price_intent:
            product = self.product_service.get_product_by_id(price_intent["product_id"], store_id)
            if product is None:
                return _message("I could not find that product in your store.")
            return _pending(
                f"Change price of {product['name']} ({product['product_id']}) to {price_intent['price']:.0f} ₸?",
                {
                    "type": "update_product_price",
                    "store_id": store_id,
                    "product_id": product["product_id"],
                    "price": price_intent["price"],
                },
            )

        description_intent = self._parse_description_update(command)
        if description_intent:
            product = self.product_service.get_product_by_id(description_intent["product_id"], store_id)
            if product is None:
                return _message("I could not find that product in your store.")
            return _pending(
                f"Update description of {product['name']} ({product['product_id']})?",
                {
                    "type": "update_product_description",
                    "store_id": store_id,
                    "product_id": product["product_id"],
                    "description": description_intent["description"],
                },
            )

        barcode_intent = self._parse_barcode_update(command)
        if barcode_intent:
            product = self.product_service.get_product_by_id(barcode_intent["product_id"], store_id)
            if product is None:
                return _message("I could not find that product in your store.")
            return _pending(
                f"Change barcode of {product['name']} ({product['product_id']}) to {barcode_intent['barcode']}?",
                {
                    "type": "update_product_barcode",
                    "store_id": store_id,
                    "product_id": product["product_id"],
                    "barcode": barcode_intent["barcode"],
                },
            )

        address_intent = self._parse_profile_update(command, "address")
        if address_intent:
            return _pending(
                f"Change store address to: {address_intent}?",
                {"type": "update_store_address", "user_id": current_user["id"], "address": address_intent},
            )

        website_intent = self._parse_profile_update(command, "website")
        if website_intent:
            return _pending(
                f"Change store website to: {website_intent}?",
                {"type": "update_store_website", "user_id": current_user["id"], "website_url": website_intent},
            )

        cheaper_than = self._parse_cheaper_than(command)
        if cheaper_than is not None:
            products = [
                product
                for product in self.product_service.list_products(store_id)
                if float(product["price"]) < cheaper_than
            ]
            return _message(_format_products(products) or f"No products cheaper than {cheaper_than:.0f} ₸.")

        if self._looks_like_analytics(command):
            analytics = self.analytics_service.get_store_analytics(store_id)
            return _message(_format_analytics(analytics))

        if self._looks_like_search(command):
            products = self.product_service.search_products(command, store_id)
            return _message(_format_products(products) or "No matching products found in your store.")

        return _message(
            "I can help search products, propose price/description/barcode edits, "
            "update store address or website after confirmation, and explain analytics. "
            "Please clarify what you want to change or search."
        )

    def confirm(self, pending_action: dict, current_user: dict, store_profile: dict) -> str:
        store_id = int(store_profile["id"])
        action_type = pending_action.get("type")

        if pending_action.get("store_id") is not None and int(pending_action["store_id"]) != store_id:
            return "Blocked: this action does not belong to your store."

        if action_type in {"update_product_price", "update_product_description", "update_product_barcode"}:
            product = self.product_service.get_product_by_id(pending_action["product_id"], store_id)
            if product is None:
                return "Product was not found in your store."

            self.product_service.update_product(
                store_id,
                product["product_id"],
                product["name"],
                pending_action.get("barcode", product.get("barcode") or ""),
                float(pending_action.get("price", product["price"])),
                pending_action.get("description", product.get("description") or ""),
            )
            return "Product updated."

        if action_type in {"update_store_address", "update_store_website"}:
            profile = store_profile
            self.store_service.save_profile(
                current_user["id"],
                profile["store_name"],
                profile.get("description") or "",
                pending_action.get("website_url", profile.get("website_url") or ""),
                pending_action.get("address", profile.get("address") or ""),
                profile.get("gps_map_url") or "",
            )
            return "Store profile updated."

        return "Unknown pending action."

    def _parse_price_update(self, command: str) -> dict | None:
        match = re.search(r"\b(P\d+)\b.*?(?:to|на|до)\s*(\d[\d\s]*)", command, re.IGNORECASE)
        if "price" not in command.lower() and "цен" not in command.lower():
            return None
        if not match:
            return None
        return {"product_id": match.group(1).upper(), "price": float(match.group(2).replace(" ", ""))}

    def _parse_description_update(self, command: str) -> dict | None:
        match = re.search(r"(?:description of|описани[ея]\s+)(.+?)\s+(?:to|and add that|на|добавь)\s+(.+)", command, re.IGNORECASE)
        if not match:
            return None
        product_ref = match.group(1).strip()
        return {"product_id": _product_id_from_text(product_ref), "description": match.group(2).strip()}

    def _parse_barcode_update(self, command: str) -> dict | None:
        match = re.search(r"\b(P\d+)\b.*?(?:barcode|штрихкод).*?(?:to|на)\s*([\w-]+)", command, re.IGNORECASE)
        if not match:
            return None
        return {"product_id": match.group(1).upper(), "barcode": match.group(2)}

    def _parse_profile_update(self, command: str, field: str) -> str | None:
        lowered = command.lower()
        if field == "address" and ("address" in lowered or "адрес" in lowered):
            match = re.search(r"(?:to|на)\s+(.+)$", command, re.IGNORECASE)
            return match.group(1).strip() if match else None
        if field == "website" and ("website" in lowered or "link" in lowered or "сайт" in lowered):
            match = re.search(r"(https?://\S+)", command, re.IGNORECASE)
            return match.group(1).strip() if match else None
        return None

    def _parse_cheaper_than(self, command: str) -> float | None:
        match = re.search(r"(?:cheaper than|дешевле)\s*(\d[\d\s]*)", command, re.IGNORECASE)
        return float(match.group(1).replace(" ", "")) if match else None

    def _looks_like_analytics(self, command: str) -> bool:
        lowered = command.lower()
        return any(term in lowered for term in ("analytics", "questions", "queries", "most", "аналит", "запрос"))

    def _looks_like_search(self, command: str) -> bool:
        lowered = command.lower()
        return any(term in lowered for term in ("show", "find", "search", "products", "покажи", "найди", "товар"))


def _product_id_from_text(text: str) -> str:
    match = re.search(r"\b(P\d+)\b", text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    cleaned = re.sub(r"[^a-zA-Z0-9]+", " ", text).strip().lower()
    if "laptop pro" in cleaned:
        return "P004"
    if "laptop basic" in cleaned:
        return "P003"
    if "smartphone a" in cleaned:
        return "P001"
    if "smartphone b" in cleaned:
        return "P002"
    return text.strip().upper()


def _pending(message: str, action: dict) -> dict:
    return {"message": message, "pending_action": action}


def _message(message: str) -> dict:
    return {"message": message, "pending_action": None}


def _format_products(products: list[dict]) -> str:
    if not products:
        return ""
    lines = ["Products in your store:"]
    for product in products[:12]:
        lines.append(
            f"- {product['product_id']}: {product['name']} — {float(product['price']):.0f} ₸. "
            f"{product.get('description') or ''}"
        )
    return "\n".join(lines)


def _format_analytics(analytics: dict) -> str:
    lines = [f"Total product-related questions: {analytics['total']}"]
    if analytics["top_mentioned"]:
        lines.append("Top mentioned products:")
        lines.extend(f"- {item['name']}: {item['count']}" for item in analytics["top_mentioned"][:5])
    if analytics["recent_queries"]:
        lines.append("Recent queries:")
        lines.extend(f"- {item['query']}" for item in analytics["recent_queries"][:5])
    return "\n".join(lines)
