import streamlit as st


def render_sidebar() -> None:
    with st.sidebar:
        st.header("AI Commerce Assistant")
        st.write("Chat for shoppers and a lightweight dashboard for stores.")

        current_user = st.session_state.get("current_user")
        if current_user is None:
            st.subheader("Guest mode")
            st.write("Use chat and product photo upload without registration.")
            return

        st.caption(f"Signed in as {current_user['username']} ({current_user['account_type']})")

        if current_user["account_type"] == "store":
            st.subheader("Store dashboard")
            options = (
                "Store Profile",
                "Product Database",
                "Product Analytics",
                "Store Assistant",
                "Preview Chat",
            )
            current_view = st.session_state.get("store_view", "Store Profile")
            if current_view not in options:
                current_view = "Store Profile"
                st.session_state["store_view"] = current_view

            selected_view = st.radio(
                "Section",
                options,
                index=options.index(current_view),
                key="store_view_selector",
                label_visibility="collapsed",
            )
            st.session_state["store_view"] = selected_view
        else:
            st.subheader("Chat tools")
            st.write("Ask product questions or attach a product photo near the chat input.")
