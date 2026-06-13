from __future__ import annotations

import streamlit as st

from config import settings


SESSION_COOKIE_NAME = "ecommerce_ai_session"


def get_cookie_manager():
    try:
        from streamlit_cookies_manager import EncryptedCookieManager
    except ModuleNotFoundError:
        return None

    cookies = st.session_state.get("_cookie_manager")
    if cookies is None:
        cookies = EncryptedCookieManager(
            prefix="",
            password=settings.COOKIE_PASSWORD,
        )
        st.session_state["_cookie_manager"] = cookies

    if not cookies.ready():
        return None
    return cookies


def get_session_cookie(cookies) -> str:
    if cookies is None:
        return ""
    return cookies.get(SESSION_COOKIE_NAME, "")


def set_session_cookie(cookies, token: str) -> None:
    if cookies is None:
        return
    cookies[SESSION_COOKIE_NAME] = token
    cookies.save()


def delete_session_cookie(cookies) -> None:
    if cookies is None:
        return
    if SESSION_COOKIE_NAME in cookies:
        del cookies[SESSION_COOKIE_NAME]
        cookies.save()
