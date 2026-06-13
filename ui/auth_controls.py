import streamlit as st

from services.account_service import AccountService
from services.cookie_service import delete_session_cookie, get_cookie_manager, get_session_cookie
from services.session_service import SessionService


def render_top_auth_controls(store_name: str | None = None) -> None:
    st.session_state.setdefault("theme_mode", "system")

    current_user = st.session_state.get("current_user")

    if current_user is None:
        theme_col, login_col, register_col = st.columns(3, vertical_alignment="center")
        with theme_col:
            _render_auth_marker()
            _render_theme_switcher()
        with login_col:
            if st.button("Login", use_container_width=True):
                st.switch_page("pages/Login.py")
        with register_col:
            if st.button("Register", use_container_width=True):
                st.switch_page("pages/Register.py")
        return

    if current_user["account_type"] == "store":
        label = store_name or current_user.get("username", "Store")
        theme_col, name_col, menu_col = st.columns(3, vertical_alignment="center")
        with theme_col:
            _render_auth_marker()
            _render_theme_switcher()
        with name_col:
            st.caption(label)
        with menu_col:
            with st.popover("...", use_container_width=True):
                if st.button("Store Dashboard", use_container_width=True):
                    st.session_state["pending_store_view"] = "Store Profile"
                    st.rerun()
                if st.button("Logout", use_container_width=True):
                    _logout()
                if st.button("Delete account", use_container_width=True):
                    st.session_state["show_delete_account_confirmation"] = True
                    st.rerun()
        _render_delete_account_confirmation(current_user)
        return

    user_label = current_user.get("email") or current_user.get("username", "User")
    theme_col, name_col, menu_col = st.columns(3, vertical_alignment="center")
    with theme_col:
        _render_auth_marker()
        _render_theme_switcher()
    with name_col:
        st.caption(user_label)
    with menu_col:
        with st.popover("...", use_container_width=True):
            if st.button("Logout", use_container_width=True):
                _logout()
            if st.button("Delete account", use_container_width=True):
                st.session_state["show_delete_account_confirmation"] = True
                st.rerun()
    _render_delete_account_confirmation(current_user)


def _logout() -> None:
    cookies = get_cookie_manager()
    token = st.session_state.get("session_token") or get_session_cookie(cookies)
    if token:
        SessionService().revoke_session(token)
    delete_session_cookie(cookies)

    for key in (
        "current_user",
        "logged_in",
        "user_id",
        "username",
        "email",
        "account_type",
        "store_id",
        "store_view",
        "store_view_selector",
        "pending_store_view",
        "session_token",
        "session_restore_checked",
    ):
        st.session_state.pop(key, None)
    st.rerun()


def _render_delete_account_confirmation(current_user: dict) -> None:
    if not st.session_state.get("show_delete_account_confirmation"):
        return

    st.error("This action is permanent. Your account and related data will be deleted.")
    with st.form("delete_account_confirmation_form"):
        confirmation_text = st.text_input("Type DELETE to confirm")
        password = st.text_input("Current password", type="password")
        submitted = st.form_submit_button(
            "Permanently delete account",
            use_container_width=True,
        )

    cancel_clicked = st.button(
        "Cancel account deletion",
        key="cancel_account_deletion",
        use_container_width=True,
    )
    if cancel_clicked:
        st.session_state["show_delete_account_confirmation"] = False
        st.rerun()

    if not submitted:
        return

    try:
        AccountService().delete_account(
            int(current_user["id"]),
            confirmation_text,
            password,
        )
        _clear_after_account_deletion()
        st.session_state["account_deleted_notice"] = True
        st.rerun()
    except ValueError as error:
        st.error(str(error))


def _clear_after_account_deletion() -> None:
    cookies = get_cookie_manager()
    token = st.session_state.get("session_token") or get_session_cookie(cookies)
    if token:
        SessionService().revoke_session(token)
    delete_session_cookie(cookies)

    for key in (
        "current_user",
        "logged_in",
        "user_id",
        "username",
        "email",
        "account_type",
        "store_id",
        "store_view",
        "store_view_selector",
        "pending_store_view",
        "session_token",
        "session_restore_checked",
        "show_delete_account_confirmation",
    ):
        st.session_state.pop(key, None)


def _render_theme_switcher() -> None:
    st.selectbox(
        "Theme",
        ("system", "light", "dark"),
        key="theme_mode",
        format_func=lambda value: value.title(),
        label_visibility="collapsed",
    )


def _render_auth_marker() -> None:
    st.markdown('<span class="top-auth-marker"></span>', unsafe_allow_html=True)
