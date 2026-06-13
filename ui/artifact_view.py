from pathlib import Path

import streamlit as st

from services.artifact_service import ArtifactService
from services.chat_service import ChatService


def render_artifacts(chat_service: ChatService, artifact_service: ArtifactService) -> None:
    st.subheader("Artifacts")

    col_docx, col_pptx = st.columns(2)

    with col_docx:
        if st.button("Create DOCX report", use_container_width=True):
            try:
                artifact_service.create_docx_from_history(chat_service.get_history())
                st.rerun()
            except RuntimeError as error:
                st.error(str(error))

    with col_pptx:
        if st.button("Create PPTX brief", use_container_width=True):
            try:
                artifact_service.create_pptx_from_history(chat_service.get_history())
                st.rerun()
            except RuntimeError as error:
                st.error(str(error))

    artifacts = artifact_service.get_artifacts()
    if not artifacts:
        st.caption("No artifacts created yet.")
        return

    for artifact in artifacts:
        file_path = Path(artifact["file_path"])
        if not file_path.exists():
            continue

        with file_path.open("rb") as file:
            st.download_button(
                label=f"Download {artifact['file_name']}",
                data=file,
                file_name=artifact["file_name"],
                mime=_mime_type(artifact["artifact_type"]),
                use_container_width=True,
            )


def _mime_type(artifact_type: str) -> str:
    if artifact_type == "pptx":
        return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
