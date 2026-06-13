import secrets

import streamlit as st

from config.settings import BASE_DIR
from services.chat_service import ChatService
from services.image_service import ImageStorageService


def render_chat(chat_service: ChatService, current_user: dict | None = None) -> None:
    user_id, session_id = _chat_scope(current_user)
    st.markdown(
        '<h1 class="page-title">AI Agent Network for E-commerce Customer Service</h1>',
        unsafe_allow_html=True,
    )

    for message in chat_service.get_history(user_id=user_id, session_id=session_id):
        with st.chat_message("user"):
            st.write(message["user_message"])
        with st.chat_message("assistant"):
            st.caption(_agent_caption(message["agent_name"], message.get("routing_reason", "")))
            st.write(message["agent_response"])

    _render_upload_notice()
    _render_clear_chat_controls(chat_service, user_id, session_id)
    _render_chat_input(chat_service, current_user, session_id)


def _render_chat_input(
    chat_service: ChatService,
    current_user: dict | None,
    session_id: str | None,
) -> None:
    quick_question = st.session_state.pop("quick_question", None)
    user_message = quick_question

    input_columns = st.columns([0.05, 0.84, 0.11], gap="small", vertical_alignment="center")
    input_version = st.session_state.setdefault("chat_input_version", 0)

    with input_columns[0]:
        st.markdown('<span class="chat-bar-marker"></span>', unsafe_allow_html=True)
        _render_photo_attach_popover()

    with input_columns[1]:
        uploaded_image_path = st.session_state.get("uploaded_image_path")
        if uploaded_image_path:
            image_file = BASE_DIR / uploaded_image_path
            if image_file.exists():
                st.image(str(image_file), caption="Uploaded image", width=120)
        typed_message = st.text_input(
            "Message",
            placeholder="Напишите вопрос интернет-магазину",
            label_visibility="collapsed",
            key=f"chat_message_input_{input_version}",
        )

    with input_columns[2]:
        send_clicked = st.button("Send", use_container_width=True)

    image_path = st.session_state.get("uploaded_image_path")
    if send_clicked and (typed_message.strip() or image_path):
        user_message = typed_message.strip() or "Find similar products based on this image."
        st.session_state["chat_input_version"] = input_version + 1

    if user_message:
        image_path = st.session_state.pop("uploaded_image_path", None)
        st.session_state.pop("uploaded_image_name", None)

        user_id = current_user["id"] if current_user else None
        agent_name, routing_reason, response = chat_service.handle_message(
            user_message,
            user_id,
            session_id,
            image_path,
        )

        with st.chat_message("user"):
            if image_path:
                image_file = BASE_DIR / image_path
                if image_file.exists():
                    st.image(str(image_file), caption="Uploaded image", width=160)
            st.write(user_message)
        with st.chat_message("assistant"):
            st.caption(_agent_caption(agent_name, routing_reason))
            st.write(response)
        st.rerun()


def _render_clear_chat_controls(
    chat_service: ChatService,
    user_id: int | None,
    session_id: str | None,
) -> None:
    if st.session_state.pop("chat_cleared_notice", False):
        st.success("Chat cleared.")

    if st.session_state.get("confirm_clear_chat"):
        st.warning("Are you sure you want to clear this chat?")
        confirm_col, cancel_col = st.columns(2)
        with confirm_col:
            if st.button("Confirm", key="confirm_clear_chat_button", use_container_width=True):
                chat_service.clear_history(user_id=user_id, session_id=session_id)
                _reset_chat_session_state()
                st.session_state["chat_cleared_notice"] = True
                st.session_state["confirm_clear_chat"] = False
                st.rerun()
        with cancel_col:
            if st.button("Cancel", key="cancel_clear_chat_button", use_container_width=True):
                st.session_state["confirm_clear_chat"] = False
                st.rerun()
        return

    if st.button("Clear chat", key="clear_chat_button"):
        st.session_state["confirm_clear_chat"] = True
        st.rerun()


def _render_photo_attach_popover() -> None:
    upload_version = st.session_state.setdefault("image_upload_widget_version", 0)

    with st.popover("Attach product photo", use_container_width=True):
        st.markdown("**Upload product photo**")
        uploaded_image = st.file_uploader(
            "Choose image",
            type=["jpg", "jpeg", "png", "webp"],
            accept_multiple_files=False,
            key=f"chat_image_uploader_{upload_version}",
        )
        st.caption("Supported: JPG, JPEG, PNG, WEBP")

        if uploaded_image is not None:
            try:
                image_path = ImageStorageService().save_chat_image(uploaded_image)
                st.session_state["uploaded_image_path"] = image_path
                st.session_state["uploaded_image_name"] = uploaded_image.name
                st.session_state["upload_notice"] = (
                    f"Фото {uploaded_image.name} добавлено к следующему сообщению."
                )
                st.session_state["image_upload_widget_version"] = upload_version + 1
                st.rerun()
            except ValueError as error:
                st.error(str(error))


def _render_upload_notice() -> None:
    upload_notice = st.session_state.pop("upload_notice", None)
    if upload_notice:
        st.success(upload_notice)


def _agent_caption(agent_name: str, routing_reason: str) -> str:
    if routing_reason:
        return f"{agent_name} | Причина: {routing_reason}"
    return agent_name


def _chat_scope(current_user: dict | None) -> tuple[int | None, str | None]:
    if current_user:
        return current_user["id"], None

    session_id = st.session_state.setdefault(
        "guest_chat_session_id",
        secrets.token_urlsafe(16),
    )
    return None, session_id


def _reset_chat_session_state() -> None:
    st.session_state["chat_input_version"] = st.session_state.get("chat_input_version", 0) + 1
    st.session_state.pop("quick_question", None)
    st.session_state.pop("uploaded_image_path", None)
    st.session_state.pop("uploaded_image_name", None)
    st.session_state.pop("upload_notice", None)
