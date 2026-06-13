import streamlit as st

from services.auth_service import AuthService
from services.email_verification_service import EmailVerificationService
from storage.database import init_database
from ui.styles import apply_styles


def _is_valid_email(email: str) -> bool:
    return bool(email) and "@" in email and "." in email and " " not in email


def main() -> None:
    st.set_page_config(page_title="Register", page_icon="AI", layout="centered")
    apply_styles()
    init_database()
    if not st.session_state.get("registration_page_loaded_logged"):
        print("registration page loaded")
        st.session_state["registration_page_loaded_logged"] = True

    _, card, _ = st.columns([1, 1.35, 1])
    with card:
        st.title("Register")

        auth_service = AuthService()
        username = st.text_input("Username")

        email_col, send_code_col = st.columns([0.72, 0.28], vertical_alignment="bottom")
        with email_col:
            email = st.text_input("Email")
        with send_code_col:
            send_code_clicked = st.button(
                "Send code",
                key="send_verification_code_button",
                use_container_width=True,
            )

        verification_code = st.text_input("Verification code")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm password", type="password")
        account_label = st.selectbox("Account type", ("Regular User", "Store"))

        st.caption(
            "Password rules: at least 8 characters; uppercase and lowercase Latin letters; "
            "at least one digit; at least one special character (!@#$%^&*()_-+=?.); "
            "only Latin letters, digits, and allowed special characters."
        )

        if send_code_clicked:
            print("send code button clicked")
            normalized_email = email.strip().lower()
            if not _is_valid_email(normalized_email):
                st.error("Enter a valid email address.")
            elif auth_service.email_exists(normalized_email):
                st.error("This email is already registered.")
            elif st.session_state.get("send_code_in_progress"):
                st.info("Verification code request is already in progress.")
            else:
                try:
                    st.session_state["send_code_in_progress"] = True
                    already_sent = (
                        st.session_state.get("verification_code_sent_email")
                        == normalized_email
                    )
                    debug_code = EmailVerificationService().send_code(normalized_email)
                    st.session_state["verification_code_sent_email"] = normalized_email
                    if already_sent:
                        st.success("A new verification code has been sent.")
                    else:
                        st.success("Verification code sent. Check your email.")
                    if debug_code:
                        st.info(f"EMAIL_DEBUG code for local development: {debug_code}")
                except ValueError as error:
                    st.error(str(error))
                finally:
                    st.session_state["send_code_in_progress"] = False

        if st.button("Create account", use_container_width=True):
            try:
                normalized_email = email.strip().lower()
                if not username.strip():
                    raise ValueError("Username is required.")
                if not _is_valid_email(normalized_email):
                    raise ValueError("Enter a valid email address.")

                auth_service.validate_registration_fields(
                    username,
                    normalized_email,
                    password,
                    confirm_password,
                    account_label,
                )

                verification_result = EmailVerificationService().verify_code(
                    normalized_email,
                    verification_code,
                )
                if verification_result.status == "missing":
                    raise ValueError(
                        "Please enter the verification code sent to your email."
                    )
                if verification_result.status == "expired":
                    raise ValueError(
                        "Verification code expired. Please request a new one."
                    )
                if verification_result.status == "used":
                    raise ValueError(
                        "Verification code was already used. Please request a new one."
                    )
                if not verification_result.is_valid:
                    raise ValueError("Invalid verification code.")

                if auth_service.username_exists(username):
                    raise ValueError("Username is already taken.")
                if auth_service.email_exists(normalized_email):
                    raise ValueError("Email is already taken.")

                auth_service.register(
                    username,
                    normalized_email,
                    password,
                    confirm_password,
                    account_label,
                )
                if verification_result.code_id is not None:
                    EmailVerificationService().mark_used(verification_result.code_id)
                st.success("Account created. Please log in.")
            except ValueError as error:
                st.error(str(error))

        if st.button("Back to Login", use_container_width=True):
            st.switch_page("pages/Login.py")

        if st.button("Back to app", use_container_width=True):
            st.switch_page("app.py")


if __name__ == "__main__":
    main()
