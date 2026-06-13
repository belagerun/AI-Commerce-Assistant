from services.auth_service import AuthService
from storage import account_deletion_repository


class AccountService:
    def __init__(self, auth_service: AuthService | None = None) -> None:
        self.auth_service = auth_service or AuthService()

    def delete_account(
        self,
        user_id: int,
        confirmation_text: str,
        password: str,
    ) -> dict:
        if confirmation_text != "DELETE":
            raise ValueError("Type DELETE to confirm account deletion.")

        if not self.auth_service.verify_user_password(user_id, password):
            raise ValueError("Current password is incorrect.")

        return account_deletion_repository.delete_user_account(user_id)
