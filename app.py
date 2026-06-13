import streamlit as st

from agents.customer_support_agent import CustomerSupportAgent
from agents.order_management_agent import OrderManagementAgent
from agents.product_recommendation_agent import ProductRecommendationAgent
from config.settings import APP_NAME
from router.agent_router import AgentRouter
from services.ai_service import AIService
from services.analytics_service import AnalyticsService
from services.artifact_service import ArtifactService
from services.auth_service import AuthService
from services.chat_service import ChatService
from services.cookie_service import get_cookie_manager, get_session_cookie, set_session_cookie
from services.database_service import DatabaseService
from services.document_service import DocumentService
from services.product_service import ProductService
from services.session_service import SessionService
from services.store_assistant_service import StoreAssistantService
from services.store_service import StoreService
from storage.database import init_database
from ui.auth_controls import render_top_auth_controls
from ui.chat_view import render_chat
from ui.sidebar import render_sidebar
from ui.store_dashboard import render_store_dashboard
from ui.styles import apply_styles


def build_services() -> tuple[
    ChatService,
    DocumentService,
    ArtifactService,
    ProductService,
    AuthService,
    StoreService,
    AnalyticsService,
    StoreAssistantService,
    SessionService,
]:
    init_database()

    ai_service = AIService()
    agents = [
        CustomerSupportAgent(ai_service),
        OrderManagementAgent(ai_service),
        ProductRecommendationAgent(ai_service),
    ]
    router = AgentRouter(agents)
    database_service = DatabaseService()
    product_service = ProductService()
    analytics_service = AnalyticsService()
    store_service = StoreService()
    session_service = SessionService()

    return (
        ChatService(router, database_service, product_service, analytics_service, ai_service),
        DocumentService(database_service),
        ArtifactService(database_service),
        product_service,
        AuthService(),
        store_service,
        analytics_service,
        StoreAssistantService(store_service, product_service, analytics_service),
        session_service,
    )


def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon="AI", layout="centered")
    apply_styles()
    _prepare_store_navigation_state()
    if st.session_state.pop("account_deleted_notice", False):
        st.success("Your account has been deleted.")

    (
        chat_service,
        document_service,
        artifact_service,
        product_service,
        auth_service,
        store_service,
        analytics_service,
        store_assistant_service,
        session_service,
    ) = build_services()
    session_service.cleanup_expired_sessions()
    cookies = get_cookie_manager()
    _save_pending_cookie(cookies)
    _restore_user_from_cookie(session_service, cookies)
    render_sidebar()

    current_user = st.session_state.get("current_user")
    store_name = None
    if current_user and current_user["account_type"] == "store":
        profile = store_service.get_profile(current_user["id"])
        if profile:
            store_name = profile.get("store_name")
            st.session_state["store_id"] = profile.get("id")
        else:
            st.session_state.pop("store_id", None)

    render_top_auth_controls(store_name)

    if current_user and current_user["account_type"] == "store":
        view = st.session_state.get("store_view", "Store Profile")
        if view == "Preview Chat":
            render_chat(chat_service, current_user)
        else:
            render_store_dashboard(
                current_user,
                store_service,
                product_service,
                analytics_service,
                store_assistant_service,
                view,
            )
    else:
        render_chat(chat_service, current_user)


def _prepare_store_navigation_state() -> None:
    if "store_view" not in st.session_state:
        st.session_state["store_view"] = "Store Profile"

    pending_store_view = st.session_state.pop("pending_store_view", None)
    if pending_store_view:
        st.session_state["store_view"] = pending_store_view
        st.session_state["store_view_selector"] = pending_store_view


def _restore_user_from_cookie(session_service: SessionService, cookies) -> None:
    if st.session_state.get("logged_in"):
        return
    if st.session_state.get("session_restore_checked"):
        return

    if cookies is None:
        return

    st.session_state["session_restore_checked"] = True
    token = get_session_cookie(cookies)
    if not token:
        return

    user = session_service.validate_session_token(token)
    if user is None:
        return

    st.session_state["current_user"] = user
    st.session_state["logged_in"] = True
    st.session_state["user_id"] = user["id"]
    st.session_state["username"] = user["username"]
    st.session_state["email"] = user.get("email", "")
    st.session_state["account_type"] = user["account_type"]
    st.session_state["session_token"] = token


def _save_pending_cookie(cookies) -> None:
    if cookies is None:
        return

    token = st.session_state.pop("pending_session_cookie", None)
    if token:
        set_session_cookie(cookies, token)


if __name__ == "__main__":
    main()
