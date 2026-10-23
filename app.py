import streamlit as st
from pathlib import Path

@st.dialog("Delete document?")
def confirm_delete(filename):
    st.write(f"Are you sure you want to delete **{filename}**?")

    col_cancel, col_delete = st.columns(2)

    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

    with col_delete:
        if st.button("Delete", type="primary", use_container_width=True):
            try:
                (Path("data/documents") / filename).unlink()
                st.toast(f"Deleted {filename}.")
                st.rerun()
            except OSError:
                st.error(f"Could not delete {filename}.")

st.set_page_config(
    page_title="Personal Research Agent",
    page_icon="🌐",
    layout="wide",
)

st.markdown(
    """
    <style>
    div[data-testid="stButton"] button {
        padding: 0px 10px;
        min-height: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Personal Research Agent")
st.caption("Research, explore, and organize your findings.")

with st.sidebar:
    st.header("Uploaded Documents")

    documents_dir = Path("data/documents")
    documents_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(
        file for file in documents_dir.iterdir()
        if file.is_file()
    )

    st.caption(f"{len(files)} document(s)")

    for file in files:
        col_name, col_delete = st.columns([5, 1])

        with col_name:
            st.markdown(f"**{file.name}**")

        with col_delete:
            if st.button(
                "X",
                key=f"delete_{file.name}",
                help=f"Delete {file.name}",
            ):
                confirm_delete(file.name)

    st.divider()

    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["txt", "md", "pdf", "docx"],
        max_upload_size=50,
        key=f"document_uploader_{st.session_state.uploader_key}",
    )

    if uploaded_file:
        destination = documents_dir / Path(uploaded_file.name).name

        try:
            if destination.exists():
                st.toast("A document with this name already exists.", icon="⚠️")
                st.session_state.uploader_key += 1
                st.rerun()
            else:
                destination.write_bytes(uploaded_file.getvalue())
                st.toast(f"{uploaded_file.name} uploaded successfully.")
                st.session_state.uploader_key += 1
                st.rerun()

        except OSError:
            st.toast(f"Could not save {uploaded_file.name}.", icon="⚠️")


# Research heading and model selection
heading_col, model_col = st.columns([3, 1])

with heading_col:
    st.subheader("What would you like to research?")

with model_col:
    model = st.selectbox(
        "Model",
        options=[
            "Gemini (default)",
            "Gemini model 2",
            "Gemini model 3",
        ],
        index=0,
        help="Choose the model for your research.",
    )
    
question = st.text_area(
    "Research question",
    placeholder="Ask a question you want to investigate...",
    height=120,
    label_visibility="collapsed",
)

st.subheader("Choose your research sources")

source = st.radio(
    "Where should the agent look?",
    options=[
        "Wikipedia",
        "Web",
        "Research Papers (arXiv)",
        "Files",
        "All Sources",
    ],
    index=4,
    horizontal=True,
    help="Choose which sources the agent should use for your research.",
    label_visibility="collapsed",
)

if st.button("Start research", type="primary"):
    if question.strip():
        st.info(
            f"Question: {question}\n\n"
            f"Selected model: {model}\n\n"
            f"Research sources: {source}\n\n"
            "Agent integration comes next."
        )
    else:
        st.toast("Please enter a research question.", icon="⚠️")