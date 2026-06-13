import re
import sqlite3

from storage import product_repository


# Development-only seed data. The production UI exposes this only when DEBUG_MODE=true.
DEMO_PRODUCTS = (
    ("P001", "Smartphone A", "4871000000011", 149000, "128 GB storage, good camera, suitable for everyday use."),
    ("P002", "Smartphone B", "4871000000028", 219000, "256 GB storage, powerful processor, suitable for gaming."),
    ("P003", "Laptop Basic", "4871000000035", 299000, "8 GB RAM, 256 GB SSD, suitable for study."),
    ("P004", "Laptop Pro", "4871000000042", 499000, "16 GB RAM, 512 GB SSD, suitable for work and programming."),
    ("P005", "Wireless Headphones", "4871000000059", 39000, "Noise cancellation, up to 30 hours battery life."),
)


class ProductService:
    def add_product(
        self,
        store_id: int,
        product_id: str,
        name: str,
        barcode: str,
        price: float,
        description: str,
        image_path: str = "",
        image_description: str = "",
        image_url: str = "",
        category: str = "",
    ) -> int:
        self._validate_product(product_id, name, price)
        return product_repository.add_product(
            store_id,
            product_id.strip(),
            name.strip(),
            barcode.strip(),
            float(price),
            description.strip(),
            image_path.strip(),
            image_description.strip(),
            image_url.strip(),
            category.strip(),
        )

    def list_products(self, store_id: int | None = None) -> list[dict[str, str | float | int]]:
        return product_repository.get_all_products(store_id)

    def get_product_by_id(
        self,
        product_id: str,
        store_id: int | None = None,
    ) -> dict[str, str | float | int] | None:
        return product_repository.get_product_by_id(product_id, store_id)

    def search_products(
        self,
        query: str,
        store_id: int | None = None,
    ) -> list[dict[str, str | float | int]]:
        products = product_repository.get_all_products(store_id)
        query_terms = _expanded_terms(query)
        budget = _extract_budget(query)

        scored_products = []
        for product in products:
            product_text = " ".join(
                str(product.get(field, ""))
                for field in ("product_id", "name", "barcode", "description", "image_description", "category")
            ).lower()
            product_terms = _expanded_terms(product_text)
            score = len(query_terms.intersection(product_terms))

            if budget is not None and float(product["price"]) <= budget:
                score += 2
            elif budget is not None and float(product["price"]) > budget:
                score -= 1

            if score > 0:
                scored_products.append((score, float(product["price"]), product))

        if not scored_products:
            return product_repository.search_products(query, store_id)

        scored_products.sort(key=lambda item: (-item[0], item[1]))
        return [product for _, _, product in scored_products]

    def update_product(
        self,
        store_id: int,
        product_id: str,
        name: str,
        barcode: str,
        price: float,
        description: str,
        image_path: str | None = None,
        image_description: str | None = None,
        image_url: str | None = None,
        category: str | None = None,
    ) -> None:
        self._validate_product(product_id, name, price)
        existing = product_repository.get_product_by_id(product_id.strip(), store_id) or {}
        product_repository.update_product(
            store_id,
            product_id.strip(),
            name.strip(),
            barcode.strip(),
            float(price),
            description.strip(),
            existing.get("image_path") if image_path is None else image_path.strip(),
            existing.get("image_description") if image_description is None else image_description.strip(),
            existing.get("image_url") if image_url is None else image_url.strip(),
            existing.get("category") if category is None else category.strip(),
        )

    def delete_product(self, product_id: str, store_id: int | None = None) -> None:
        product_repository.delete_product(product_id, store_id)

    def load_demo_products(self, store_id: int) -> int:
        """Development/debug helper. Do not expose in production UI."""
        added_count = 0

        for product_id, name, barcode, price, description in DEMO_PRODUCTS:
            try:
                self.add_product(store_id, product_id, name, barcode, price, description)
                added_count += 1
            except sqlite3.IntegrityError:
                continue

        return added_count

    def format_products_for_agent(
        self,
        query: str,
        limit: int = 5,
    ) -> str:
        products = self.search_products(query)[:limit]
        return self.format_product_list_for_agent(products)

    def format_product_list_for_agent(self, products: list[dict[str, str | float | int]]) -> str:
        if not products:
            return ""

        lines = [
            "Product database context:",
            "If you use these products, clearly say that the recommendation is based on the product database.",
        ]

        for product in products:
            details = [
                f"Product ID: {product['product_id']}",
                f"Name: {product['name']}",
                f"Barcode: {product.get('barcode') or 'N/A'}",
                f"Price: {product['price']:.0f} ₸",
                f"Description: {product.get('description') or ''}",
                f"Store: {product.get('store_name') or 'Store'}",
            ]
            if product.get("image_description"):
                details.append(f"Product image description: {product['image_description']}")
            if product.get("image_path"):
                details.append("Product has a store-uploaded image")
            if product.get("image_url"):
                details.append(f"Product image URL: {product['image_url']}")
            if product.get("category"):
                details.append(f"Category: {product['category']}")
            if product.get("website_url"):
                details.append(f"Website: {product['website_url']}")
            if product.get("address"):
                details.append(f"Address: {product['address']}")
            if product.get("gps_map_url"):
                details.append(f"GPS / Map link: {product['gps_map_url']}")
            lines.append("- " + "; ".join(details))

        return "\n".join(lines)

    def _validate_product(self, product_id: str, name: str, price: float) -> None:
        if not product_id.strip():
            raise ValueError("Product ID is required.")
        if not name.strip():
            raise ValueError("Product name is required.")
        if float(price) < 0:
            raise ValueError("Price cannot be negative.")


def _expanded_terms(text: str) -> set[str]:
    base_terms = {
        term
        for term in re.findall(r"[\wа-яА-ЯёЁ]+", (text or "").lower())
        if len(term) > 2
    }
    expanded = set(base_terms)

    for term in base_terms:
        if len(term) > 5:
            expanded.add(term[:5])
        expanded.update(_synonyms(term))

    return expanded


def _synonyms(term: str) -> set[str]:
    synonyms = {
        "смартфон": {"smartphone", "phone"},
        "смартфона": {"smartphone", "phone"},
        "смартфоны": {"smartphone", "phone"},
        "телефон": {"smartphone", "phone"},
        "ноутбук": {"laptop"},
        "ноутбука": {"laptop"},
        "ноутбуки": {"laptop"},
        "наушники": {"headphones", "wireless"},
        "наушников": {"headphones", "wireless"},
        "учёбы": {"study", "basic"},
        "учебы": {"study", "basic"},
        "игр": {"gaming"},
        "работы": {"work", "programming"},
    }
    return synonyms.get(term, set())


def _extract_budget(query: str) -> float | None:
    budget_markers = ("до", "under", "below", "less than")
    lowered_query = (query or "").lower()

    if not any(marker in lowered_query for marker in budget_markers):
        return None

    numbers = re.findall(r"\d[\d\s]*", lowered_query)
    if not numbers:
        return None

    return float(numbers[-1].replace(" ", ""))
