from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from storage import session_repository


SESSION_DAYS = 7


class SessionService:
    def create_session(self, user_id: int) -> str:
        token = secrets.token_urlsafe(32)
        now = _utc_now()
        expires_at = now + timedelta(days=SESSION_DAYS)
        session_repository.insert_session(
            user_id,
            self.hash_token(token),
            _to_iso(now),
            _to_iso(expires_at),
        )
        return token

    def hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def validate_session_token(self, token: str) -> dict | None:
        if not token:
            return None

        row = session_repository.find_valid_session(
            self.hash_token(token),
            _to_iso(_utc_now()),
        )
        if row is None:
            return None

        return {
            "id": row["id"],
            "username": row["username"],
            "email": row.get("email") or "",
            "account_type": row["account_type"],
        }

    def revoke_session(self, token: str) -> None:
        if token:
            session_repository.revoke_session(self.hash_token(token))

    def cleanup_expired_sessions(self) -> None:
        session_repository.cleanup_expired_sessions(_to_iso(_utc_now()))


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_iso(value: datetime) -> str:
    return value.isoformat()
