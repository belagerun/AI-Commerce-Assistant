import streamlit as st

from services.auth_service import AuthService
from services.cookie_service import get_cookie_manager, set_session_cookie
from services.session_service import SessionService
from storage.database import init_database
from ui.styles import apply_styles


def main() -> None:
    st.set_page_config(page_title="Login", page_icon="AI", layout="centered")
    apply_styles()
    init_database()
    cookies = get_cookie_manager()

    _, card, _ = st.columns([1, 1.35, 1])
    with card:
        st.title("Login")
        st.caption("Sign in with username or email.")

        auth_service = AuthService()
        session_service = SessionService()
        login = st.text_input("Username or email")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            try:
                user = auth_service.login(login, password)
                token = session_service.create_session(user["id"])
                set_session_cookie(cookies, token)
                _set_current_user(user, token)
                if cookies is None:
                    st.session_state["pending_session_cookie"] = token
                st.success("Logged in.")
                st.switch_page("app.py")
            except ValueError as error:
                st.error(str(error))

        col_register, col_forgot = st.columns(2)
        with col_register:
            if st.button("Create account", use_container_width=True):
                st.switch_page("pages/Register.py")
        with col_forgot:
            if st.button("Forgot password?", use_container_width=True):
                st.session_state["show_recovery"] = True

        if st.session_state.get("show_recovery"):
            st.divider()
            st.subheader("Password recovery")
            recovery_email = st.text_input("Email", key="recovery_email")
            if st.button("Send recovery instructions", use_container_width=True):
                # TODO: implement real email verification and password reset tokens later.
                if auth_service.email_exists(recovery_email):
                    st.info("Password recovery is not implemented yet, but this email was found.")
                else:
                    st.info(
                        "If this email is registered, recovery instructions will be available "
                        "in a future version."
                    )

        if st.button("Back to app", use_container_width=True):
            st.switch_page("app.py")


def _set_current_user(user: dict, token: str = "") -> None:
    st.session_state["current_user"] = user
    st.session_state["logged_in"] = True
    st.session_state["user_id"] = user["id"]
    st.session_state["username"] = user["username"]
    st.session_state["email"] = user.get("email", "")
    st.session_state["account_type"] = user["account_type"]
    st.session_state["session_token"] = token
    st.session_state["session_restore_checked"] = True


if __name__ == "__main__":
    main()
