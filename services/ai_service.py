import base64
from pathlib import Path

from config.settings import AI_API_KEY, AI_MODEL, AI_VISION_MODEL, BASE_DIR


class AIService:
    def __init__(self) -> None:
        self.api_key = AI_API_KEY
        self.model = AI_MODEL
        self.vision_model = AI_VISION_MODEL
        self.client = self._create_client()

    def _create_client(self):
        if not self.api_key:
            return None

        try:
            from openai import OpenAI
        except ImportError:
            return None

        try:
            return OpenAI(api_key=self.api_key)
        except TypeError as error:
            if "proxies" not in str(error):
                raise

            try:
                import httpx
            except ImportError:
                return None

            return OpenAI(api_key=self.api_key, http_client=httpx.Client())

    def generate_response(self, system_prompt: str, user_message: str) -> str:
        if self.client is None:
            return (
                "AI API is not configured. Install dependencies, add AI_API_KEY "
                "to the .env file, then restart the Streamlit app."
            )

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.4,
            )
        except Exception as error:
            return f"AI API request failed: {error}"

        return completion.choices[0].message.content or "Не удалось получить ответ от AI."

    def describe_image(self, image_path: str) -> str:
        if self.client is None:
            return ""

        path = _safe_image_path(image_path)
        if path is None or not path.exists():
            return ""

        try:
            image_bytes = path.read_bytes()
            mime_type = _mime_type(path)
            data_url = f"data:{mime_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
            completion = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Describe this product image briefly for e-commerce search. "
                                    "Mention product type, color, visible features, and likely use. "
                                    "Do not invent brand names."
                                ),
                            },
                            {"type": "image_url", "image_url": {"url": data_url}},
                        ],
                    }
                ],
                temperature=0.2,
            )
        except Exception:
            return ""

        return completion.choices[0].message.content or ""


def _safe_image_path(image_path: str) -> Path | None:
    candidate = (BASE_DIR / image_path).resolve()
    base = BASE_DIR.resolve()
    if base not in candidate.parents and candidate != base:
        return None
    return candidate


def _mime_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    return "image/png"
