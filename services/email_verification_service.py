from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from config import settings
from services.email_service import SMTP_CONFIG_ERROR, EmailService
from storage import email_verification_repository


CODE_EXPIRATION_MINUTES = 10


@dataclass(frozen=True)
class VerificationResult:
    status: str
    code_id: int | None = None

    @property
    def is_valid(self) -> bool:
        return self.status == "valid"


class EmailVerificationService:
    def __init__(self, email_service: EmailService | None = None) -> None:
        self.email_service = email_service or EmailService()

    def send_code(self, email: str) -> str | None:
        normalized_email = _normalize_email(email)
        if not settings.EMAIL_DEBUG and not self.email_service.is_configured():
            raise ValueError(SMTP_CONFIG_ERROR)

        code = _generate_code()
        now = _utc_now()
        expires_at = now + timedelta(minutes=CODE_EXPIRATION_MINUTES)

        email_verification_repository.invalidate_old_codes(normalized_email)
        email_verification_repository.create_verification_code(
            normalized_email,
            _hash_code(normalized_email, code),
            _to_iso(expires_at),
            _to_iso(now),
        )

        if settings.EMAIL_DEBUG:
            print(f"email debug mode active for {normalized_email}; verification code: {code}")
            return code

        try:
            self.email_service.send_verification_email(normalized_email, code)
        except ValueError:
            email_verification_repository.invalidate_old_codes(normalized_email)
            raise

        return None

    def verify_code(self, email: str, plain_code: str) -> VerificationResult:
        normalized_email = _normalize_email(email)
        cleaned_code = plain_code.strip()

        if not cleaned_code:
            return VerificationResult("missing")

        row = email_verification_repository.get_latest_valid_code(normalized_email)
        if row is None:
            return VerificationResult("invalid")

        code_id = int(row["id"])
        if int(row.get("used") or 0):
            return VerificationResult("used", code_id)

        expires_at = _from_iso(row["expires_at"])
        if expires_at <= _utc_now():
            return VerificationResult("expired", code_id)

        expected_hash = row["code_hash"]
        candidate_hash = _hash_code(normalized_email, cleaned_code)
        if not secrets.compare_digest(expected_hash, candidate_hash):
            return VerificationResult("invalid", code_id)

        return VerificationResult("valid", code_id)

    def mark_used(self, code_id: int) -> None:
        email_verification_repository.mark_code_used(code_id)


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _hash_code(email: str, code: str) -> str:
    return hashlib.sha256(f"{email}:{code}".encode("utf-8")).hexdigest()


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_iso(value: datetime) -> str:
    return value.isoformat()


def _from_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed
