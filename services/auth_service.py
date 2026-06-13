import hashlib
import re
import secrets
import sqlite3

from storage import auth_repository


ACCOUNT_LABELS = {
    "Regular User": "user",
    "Store": "store",
}
ALLOWED_PASSWORD_SPECIALS = "!@#$%^&*()_-+=?."
PASSWORD_ALLOWED_PATTERN = re.compile(rf"^[A-Za-z0-9{re.escape(ALLOWED_PASSWORD_SPECIALS)}]+$")
PASSWORD_REQUIREMENTS_MESSAGE = (
    "Password must:\n"
    "- be at least 8 characters long;\n"
    "- contain uppercase and lowercase Latin letters;\n"
    "- contain at least one digit;\n"
    "- contain at least one special character (!@#$%^&*()_-+=?.);\n"
    "- contain only Latin letters, digits, and allowed special characters."
)


class AuthService:
    def register(
        self,
        username: str,
        email: str,
        password: str,
        confirm_password: str,
        account_label: str,
    ) -> dict:
        username, email, account_type = self.validate_registration_fields(
            username,
            email,
            password,
            confirm_password,
            account_label,
        )

        password_hash = _hash_password(password)

        try:
            user_id = auth_repository.create_user(username, email, password_hash, account_type)
        except sqlite3.IntegrityError as error:
            if auth_repository.get_user_by_username(username):
                raise ValueError("Username is already taken.") from error
            if auth_repository.get_user_by_email(email):
                raise ValueError("Email is already taken.") from error
            raise ValueError("Username or email is already taken.") from error

        return {
            "id": user_id,
            "username": username,
            "email": email,
            "account_type": account_type,
        }

    def validate_registration_fields(
        self,
        username: str,
        email: str,
        password: str,
        confirm_password: str,
        account_label: str,
    ) -> tuple[str, str, str]:
        username = username.strip()
        email = email.strip().lower()
        account_type = ACCOUNT_LABELS.get(account_label, account_label)

        if account_type not in {"user", "store"}:
            raise ValueError("Invalid account type.")
        if not username:
            raise ValueError("Username is required.")
        if not _is_valid_email(email):
            raise ValueError("Email format is invalid.")
        if password != confirm_password:
            raise ValueError("Passwords do not match.")
        _validate_password(password)

        return username, email, account_type

    def login(self, login: str, password: str) -> dict:
        cleaned_login = login.strip()
        user = auth_repository.get_user_by_login(
            cleaned_login.lower() if "@" in cleaned_login else cleaned_login
        )
        if user is None or not _verify_password(password, user["password_hash"]):
            raise ValueError("Invalid username or password.")

        return {
            "id": user["id"],
            "username": user["username"],
            "email": user.get("email") or "",
            "account_type": user["account_type"],
        }

    def email_exists(self, email: str) -> bool:
        return auth_repository.get_user_by_email(email.strip().lower()) is not None

    def username_exists(self, username: str) -> bool:
        return auth_repository.get_user_by_username(username.strip()) is not None

    def verify_user_password(self, user_id: int, password: str) -> bool:
        user = auth_repository.get_user_by_id(user_id)
        if user is None:
            return False
        return _verify_password(password, user["password_hash"])


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
    return f"{salt}${digest}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, digest = stored_hash.split("$", 1)
    except ValueError:
        return False

    candidate = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
    return secrets.compare_digest(candidate, digest)


def _is_valid_email(email: str) -> bool:
    return bool(email) and "@" in email and "." in email and " " not in email


def _validate_password(password: str) -> None:
    if len(password) < 8:
        raise ValueError(PASSWORD_REQUIREMENTS_MESSAGE)
    if not PASSWORD_ALLOWED_PATTERN.fullmatch(password):
        raise ValueError(PASSWORD_REQUIREMENTS_MESSAGE)
    if not re.search(r"[A-Z]", password):
        raise ValueError(PASSWORD_REQUIREMENTS_MESSAGE)
    if not re.search(r"[a-z]", password):
        raise ValueError(PASSWORD_REQUIREMENTS_MESSAGE)
    if not re.search(r"\d", password):
        raise ValueError(PASSWORD_REQUIREMENTS_MESSAGE)
    if not re.search(rf"[{re.escape(ALLOWED_PASSWORD_SPECIALS)}]", password):
        raise ValueError(PASSWORD_REQUIREMENTS_MESSAGE)
