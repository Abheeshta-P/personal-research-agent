import streamlit as st
from pathlib import Path
from langchain_core.messages import HumanMessage
from graphs.main_graph import graph
from agents.model import model
from tools.research import set_active_source
from tools.files import read_file
from output.save_research import markdown_to_text, create_filename

# --- Helper functions ---

def extract_response_text(message) -> str:
    """Safely extract plain text from an AIMessage or ToolMessage."""
    if hasattr(message, "text") and message.text:
        return str(message.text)
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
            elif isinstance(part, str):
                parts.append(part)
        return "\n".join(parts)
    return str(content)

SOURCE_MAPPING = {
    "Wikipedia": "Wikipedia",
    "Web": "Web",
    "Research Papers (arXiv)": "Research Papers",
    "Files": "Files",
    "All Sources": "All",
}

AVAILABLE_MODELS = {
    "Gemini 3.1 Flash Lite (Default)": "gemini-3.1-flash-lite",
    "Gemini 2.5 Flash": "gemini-2.5-flash",
}

# --- Dialogs ---

@st.dialog("Document Preview", width="large")
def view_document(filename: str):
    file_path = Path("data/documents") / filename
    st.write(f"**{filename}**")
    try:
        content = read_file(file_path)
        if content and content.strip():
            with st.container(height=450, border=True):
                st.markdown(content)
        else:
            st.info(f"'{filename}' is empty or contains no readable text.")
    except Exception as e:
        st.error(f"Could not read {filename}: {e}")

@st.dialog("Delete document?")
def confirm_delete(filename: str):
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

# --- Page Configuration ---

st.set_page_config(
    page_title="Personal Research Agent",
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

# --- Sidebar: Document Management ---

with st.sidebar:
    st.header("Documents")

    # 1. Upload placed at the top for immediate access
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0

    MAX_FILES_PER_BATCH = 20

    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["txt", "md", "pdf", "docx"],
        accept_multiple_files=True,
        max_upload_size=50,
        key=f"document_uploader_{st.session_state.uploader_key}",
        help="Upload up to 20 TXT, Markdown, PDF, or Word documents (max 50 MB each).",
    )

    documents_dir = Path("data/documents")
    documents_dir.mkdir(parents=True, exist_ok=True)

    if uploaded_files:
        if len(uploaded_files) > MAX_FILES_PER_BATCH:
            st.toast(f"Please upload a maximum of {MAX_FILES_PER_BATCH} files at a time.")
        else:
            added = 0
            for uploaded_file in uploaded_files:
                destination = documents_dir / Path(uploaded_file.name).name
                try:
                    if destination.exists():
                        st.toast(f"'{uploaded_file.name}' already exists.")
                    else:
                        destination.write_bytes(uploaded_file.getvalue())
                        added += 1
                except OSError:
                    st.toast(f"Could not save {uploaded_file.name}.")

            if added > 0:
                st.toast(f"Uploaded {added} new document(s) successfully.")
                st.session_state.uploader_key += 1
                st.rerun()

    # 2. Document Library with scroll container, search filter, and safety cap
    all_files = sorted(
        file for file in documents_dir.iterdir()
        if file.is_file()
    )

    st.subheader(f"Library ({len(all_files)})")

    # Search filter when library has multiple files
    if len(all_files) > 5:
        search_query = st.text_input(
            "Search documents",
            placeholder="Search document name...",
            label_visibility="collapsed",
            key="file_search_filter",
        ).strip().lower()
        visible_files = [f for f in all_files if search_query in f.name.lower()]
    else:
        visible_files = all_files

    # Display cap to prevent browser lag with large collections
    MAX_DISPLAY_FILES = 50
    display_files = visible_files[:MAX_DISPLAY_FILES]

    if len(visible_files) > MAX_DISPLAY_FILES:
        st.caption(f"Showing first {MAX_DISPLAY_FILES} of {len(visible_files)} matches")
    elif not visible_files and all_files:
        st.caption("No matching documents found.")
    elif not all_files:
        st.caption("No documents uploaded yet.")

    # Scrollable container keeps sidebar height tidy
    with st.container(height=300):
        for file in display_files:
            col_name, col_delete = st.columns([5, 1])

            with col_name:
                if st.button(
                    file.name,
                    key=f"view_{file.name}",
                    help=f"View {file.name}",
                    use_container_width=True,
                ):
                    view_document(file.name)

            with col_delete:
                if st.button(
                    "X",
                    key=f"delete_{file.name}",
                    help=f"Delete {file.name}",
                ):
                    confirm_delete(file.name)

# --- Main Page Layout ---

st.title("Personal Research Agent")
st.caption("Autonomous multi-source research powered by Gemini, LangChain, and LangGraph.")

is_running = st.session_state.get("is_researching", False)
has_result = "research_result" in st.session_state
is_locked = is_running or has_result

# Heading and model selection
heading_col, model_col = st.columns([3, 1])

with heading_col:
    st.subheader("What would you like to research?")

with model_col:
    model_display_name = st.selectbox(
        "Model",
        options=list(AVAILABLE_MODELS.keys()),
        index=0,
        disabled=is_locked,
        help="Choose the Gemini model for synthesis.",
    )
    chosen_model_id = AVAILABLE_MODELS[model_display_name]
    if hasattr(model, "model"):
        model.model = chosen_model_id

if is_running:
    question_value = st.session_state.get("active_question", "")
elif has_result:
    question_value = st.session_state["research_result"]["question"]
else:
    question_value = ""

question = st.text_area(
    "Research question",
    value=question_value,
    placeholder="Ask a question you want to investigate (e.g., 'What is transformer architecture?', 'Who is Alan Turing?')...",
    height=100,
    disabled=is_locked,
    label_visibility="collapsed",
)

st.subheader("Choose your research source")

source_options = [
    "All Sources",
    "Wikipedia",
    "Web",
    "Research Papers (arXiv)",
    "Files",
]

# Reflect the selected source if researching or result is present
default_source_idx = 0
if is_running:
    used_source = st.session_state.get("active_source", "All")
    for idx, opt in enumerate(source_options):
        if SOURCE_MAPPING.get(opt) == used_source:
            default_source_idx = idx
            break
elif has_result:
    used_source = st.session_state["research_result"].get("source", "All")
    for idx, opt in enumerate(source_options):
        if SOURCE_MAPPING.get(opt) == used_source:
            default_source_idx = idx
            break

source_label = st.radio(
    "Where should the agent look?",
    options=source_options,
    index=default_source_idx,
    horizontal=True,
    disabled=is_locked,
    help="Select which source tools the research agent should investigate.",
    label_visibility="collapsed",
)

target_source = SOURCE_MAPPING.get(source_label, "All")

button_label = "Researching..." if is_running else "Start research"

col_action, col_clear = st.columns([4, 1])

with col_action:
    start_clicked = st.button(
        button_label,
        type="primary",
        disabled=is_locked,
        use_container_width=True,
    )

with col_clear:
    if st.button("Clear", disabled=is_running, use_container_width=True):
        st.session_state.pop("research_result", None)
        st.session_state.pop("active_question", None)
        st.session_state.pop("active_source", None)
        st.session_state.is_researching = False
        st.rerun()

# --- Execution ---

if start_clicked:
    if not question.strip():
        st.toast("Please enter a research question.")
    else:
        st.session_state.is_researching = True
        st.session_state.active_question = question.strip()
        st.session_state.active_source = target_source
        st.rerun()

if is_running:
    active_question = st.session_state.get("active_question", "")
    active_source = st.session_state.get("active_source", "All")

    with st.spinner(f"Agent researching with source '{active_source}'..."):
        try:
            # Set active source override for non-interactive research tool execution
            set_active_source(active_source)

            result = graph.invoke({
                "messages": [
                    HumanMessage(content=active_question)
                ],
            })

            last_message = result["messages"][-1]
            answer = extract_response_text(last_message)

            is_failed = False
            if isinstance(answer, str) and answer.startswith("RESEARCH_FAILED:"):
                is_failed = True
                answer = answer.replace("RESEARCH_FAILED:", "").strip()

            st.session_state["research_result"] = {
                "question": active_question,
                "answer": answer,
                "is_failed": is_failed,
                "source": active_source,
            }

        except Exception as e:
            st.error(f"Error during research execution: {e}")
        finally:
            set_active_source(None)
            st.session_state.is_researching = False
            st.rerun()

# --- Display Results ---

if "research_result" in st.session_state:
    res = st.session_state["research_result"]

    st.divider()

    if res["is_failed"]:
        st.warning(f"Research incomplete: {res['answer']}")
    else:
        st.subheader("Research Findings")

        with st.container(height=450, border=True):
            st.markdown(res["answer"])

        st.caption("Note: AI-generated research may contain inaccuracies. Please verify with cited sources.")

        st.markdown("---")

        col_dl_md, col_dl_txt = st.columns(2)

        with col_dl_md:
            st.download_button(
                "Download Markdown (.md)",
                data=res["answer"],
                file_name=create_filename(res["question"], "md"),
                mime="text/markdown",
                use_container_width=True,
            )

        with col_dl_txt:
            st.download_button(
                "Download Text (.txt)",
                data=markdown_to_text(res["answer"]),
                file_name=create_filename(res["question"], "txt"),
                mime="text/plain",
                use_container_width=True,
            )
