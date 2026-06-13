import streamlit as st


def apply_styles() -> None:
    theme_mode = st.session_state.setdefault("theme_mode", "system")
    inject_global_styles(theme_mode)


def inject_global_styles(theme_mode: str = "system") -> None:
    theme_class = {
        "light": "theme-light",
        "dark": "theme-dark",
    }.get(theme_mode, "theme-system")

    css = """
        <style>
        header[data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        #MainMenu,
        footer,
        [data-testid="stSidebarNav"] {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }

        :root {
            --bg-color: #0b0f17;
            --sidebar-bg: #111827;
            --panel-bg: rgba(17, 24, 39, 0.92);
            --input-bg: #1f2937;
            --button-bg: #111827;
            --button-hover-bg: #172033;
            --text-color: #f9fafb;
            --muted-text-color: #cbd5e1;
            --placeholder-color: #94a3b8;
            --border-color: #374151;
            --accent-color: #38bdf8;
            --shadow-color: rgba(0, 0, 0, 0.28);
        }

        @media (prefers-color-scheme: light) {
            :root {
                --bg-color: #f8fafc;
                --sidebar-bg: #ffffff;
                --panel-bg: rgba(255, 255, 255, 0.94);
                --input-bg: #ffffff;
                --button-bg: #f8fafc;
                --button-hover-bg: #eef2f7;
                --text-color: #111827;
                --muted-text-color: #475569;
                --placeholder-color: #6b7280;
                --border-color: #d1d5db;
                --accent-color: #0284c7;
                --shadow-color: rgba(15, 23, 42, 0.10);
            }
        }

        .stApp.theme-light,
        .stApp:has(.theme-light) {
            --bg-color: #f8fafc;
            --sidebar-bg: #ffffff;
            --panel-bg: rgba(255, 255, 255, 0.94);
            --input-bg: #ffffff;
            --button-bg: #f8fafc;
            --button-hover-bg: #eef2f7;
            --text-color: #111827;
            --muted-text-color: #475569;
            --placeholder-color: #6b7280;
            --border-color: #d1d5db;
            --accent-color: #0284c7;
            --shadow-color: rgba(15, 23, 42, 0.10);
        }

        .stApp.theme-dark,
        .stApp:has(.theme-dark) {
            --bg-color: #0b0f17;
            --sidebar-bg: #111827;
            --panel-bg: rgba(17, 24, 39, 0.92);
            --input-bg: #1f2937;
            --button-bg: #111827;
            --button-hover-bg: #172033;
            --text-color: #f9fafb;
            --muted-text-color: #cbd5e1;
            --placeholder-color: #94a3b8;
            --border-color: #374151;
            --accent-color: #38bdf8;
            --shadow-color: rgba(0, 0, 0, 0.28);
        }

        .stApp {
            background: var(--bg-color);
            color: var(--text-color);
        }

        .stApp,
        .stApp p,
        .stApp span,
        .stApp label,
        .stApp div,
        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp h4,
        .stApp h5,
        .stApp h6,
        .stMarkdown,
        .stCaptionContainer {
            color: var(--text-color);
        }

        .block-container {
            max-width: 1100px;
            margin-left: auto;
            margin-right: auto;
            padding-top: 7rem;
            padding-bottom: 7rem;
        }

        .page-title {
            margin: 0 0 2.75rem 0;
            max-width: 820px;
            color: var(--text-color);
            font-size: clamp(2.25rem, 4vw, 3.35rem);
            line-height: 1.18;
            font-weight: 800;
            letter-spacing: 0;
        }

        .top-auth-marker,
        .chat-bar-marker {
            display: none;
        }

        div[data-testid="stHorizontalBlock"]:has(.top-auth-marker) {
            position: fixed;
            top: 24px;
            right: 28px;
            z-index: 1000;
            width: auto;
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 8px;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            background: var(--panel-bg);
            box-shadow: 0 12px 36px var(--shadow-color);
            backdrop-filter: blur(12px);
        }

        div[data-testid="stHorizontalBlock"]:has(.top-auth-marker) > div[data-testid="column"] {
            flex: 0 0 auto;
            min-width: 0;
            padding: 0;
        }

        div[data-testid="stHorizontalBlock"]:has(.top-auth-marker) > div[data-testid="column"]:nth-of-type(1) {
            width: 150px;
        }

        div[data-testid="stHorizontalBlock"]:has(.top-auth-marker) > div[data-testid="column"]:nth-of-type(2),
        div[data-testid="stHorizontalBlock"]:has(.top-auth-marker) > div[data-testid="column"]:nth-of-type(3) {
            width: 104px;
        }

        div[data-testid="stHorizontalBlock"]:has(.top-auth-marker) [data-testid="stVerticalBlock"],
        div[data-testid="stHorizontalBlock"]:has(.top-auth-marker) [data-testid="stElementContainer"],
        div[data-testid="stHorizontalBlock"]:has(.top-auth-marker) [data-testid="stButton"],
        div[data-testid="stHorizontalBlock"]:has(.top-auth-marker) [data-testid="stSelectbox"] {
            width: 100%;
            margin: 0;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid var(--border-color);
            background: var(--sidebar-bg);
            color: var(--text-color);
        }

        [data-testid="stSidebar"] * {
            color: var(--text-color);
        }

        [data-testid="stChatMessage"] {
            border-radius: 10px;
            padding: 0.75rem;
            background: transparent;
        }

        .auth-card {
            max-width: 480px;
            margin: 3rem auto 0 auto;
            padding: 1.5rem;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            background: var(--panel-bg);
        }

        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) {
            position: sticky;
            bottom: 1rem;
            z-index: 900;
            width: 100%;
            display: flex;
            align-items: center;
            gap: 12px;
            margin-top: 2rem;
            padding: 8px;
            border: 1px solid var(--border-color);
            border-radius: 14px;
            background: var(--panel-bg);
            box-shadow: 0 12px 36px var(--shadow-color);
            backdrop-filter: blur(12px);
            box-sizing: border-box;
        }

        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) > div[data-testid="column"] {
            min-width: 0;
            padding: 0;
        }

        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) > div[data-testid="column"]:nth-of-type(1) {
            flex: 0 0 44px;
            width: 44px;
        }

        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) > div[data-testid="column"]:nth-of-type(2) {
            flex: 1 1 auto;
            width: auto;
        }

        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) > div[data-testid="column"]:nth-of-type(3) {
            flex: 0 0 100px;
            width: 100px;
        }

        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) [data-testid="stVerticalBlock"],
        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) [data-testid="stElementContainer"],
        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) [data-testid="stTextInput"],
        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) [data-testid="stButton"],
        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) [data-testid="stPopover"],
        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) div[data-baseweb="input"],
        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) div[data-baseweb="base-input"] {
            width: 100%;
            min-width: 0;
            margin: 0;
            box-sizing: border-box;
        }

        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) input[aria-label="Message"] {
            width: 100%;
        }

        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) div[data-testid="stPopover"] button {
            width: 44px;
            min-width: 44px;
            height: 44px;
            min-height: 44px;
            position: relative;
            overflow: hidden;
            color: transparent;
            font-size: 0;
            line-height: 0;
            padding: 0;
            border-radius: 10px;
            white-space: nowrap;
        }

        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) div[data-testid="stPopover"] button::before,
        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) div[data-testid="stPopover"] button::after {
            content: "";
            position: absolute;
            left: 50%;
            top: 50%;
            width: 16px;
            height: 2px;
            border-radius: 999px;
            background: var(--text-color);
            transform: translate(-50%, -50%);
        }

        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) div[data-testid="stPopover"] button::after {
            transform: translate(-50%, -50%) rotate(90deg);
        }

        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) div[data-testid="stPopover"] button p,
        div[data-testid="stHorizontalBlock"]:has(.chat-bar-marker) div[data-testid="stPopover"] button div {
            display: none;
        }

        button,
        .stButton button,
        button[kind],
        [data-testid="stBaseButton-secondary"],
        [data-testid="stBaseButton-primary"],
        div[data-baseweb="select"] > div {
            height: 44px;
            min-height: 44px;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            background: var(--button-bg);
            color: var(--text-color);
            font-size: 0.95rem;
            line-height: 1.2;
        }

        .stButton button:hover,
        button[kind]:hover,
        [data-testid="stBaseButton-secondary"]:hover,
        [data-testid="stBaseButton-primary"]:hover {
            background: var(--button-hover-bg);
            border-color: var(--accent-color);
            color: var(--text-color);
        }

        input,
        textarea,
        [data-baseweb="input"] input,
        [data-baseweb="textarea"] textarea,
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        div[data-baseweb="base-input"] input,
        div[data-baseweb="base-input"] textarea,
        [contenteditable="true"] {
            height: 44px;
            min-height: 44px;
            box-sizing: border-box;
            background: var(--input-bg);
            color: var(--text-color) !important;
            border-color: var(--border-color);
            caret-color: var(--text-color);
            font-size: 0.95rem;
            line-height: 1.2;
        }

        [data-baseweb="input"] > div,
        [data-baseweb="textarea"] > div,
        div[data-baseweb="base-input"],
        [data-testid="stTextInput"] div,
        [data-testid="stTextArea"] div,
        [data-baseweb="select"] > div,
        [data-baseweb="popover"] {
            background: var(--input-bg);
            color: var(--text-color);
            border-color: var(--border-color);
        }

        input::placeholder,
        textarea::placeholder,
        [data-baseweb="input"] input::placeholder,
        [data-baseweb="textarea"] textarea::placeholder,
        [data-testid="stTextInput"] input::placeholder,
        [data-testid="stTextArea"] textarea::placeholder {
            color: var(--placeholder-color) !important;
            opacity: 1;
        }

        input:focus,
        textarea:focus,
        [contenteditable="true"]:focus {
            color: var(--text-color) !important;
            caret-color: var(--text-color);
            outline-color: var(--accent-color);
        }

        [data-baseweb="select"] span,
        [data-baseweb="popover"] * {
            color: var(--text-color);
        }

        [data-testid="stFileUploader"] section,
        [data-testid="stFileUploader"] button {
            background: var(--panel-bg);
            color: var(--text-color);
            border-color: var(--border-color);
        }
        </style>
        """
    st.markdown(
        css + f'<div class="{theme_class}"></div>',
        unsafe_allow_html=True,
    )
