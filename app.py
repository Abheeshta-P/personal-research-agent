import streamlit as st

st.set_page_config(
    page_title="Personal Research Agent",
    page_icon="🌐",
    layout="wide",
)

st.title("Personal Research Agent")
st.caption("Research, explore, and organize your findings.")

with st.sidebar:
    st.header("Your Documents")
    st.caption("Uploaded files will appear here.")

    st.button(
        "Upload documents",
        use_container_width=True,
        disabled=True,
        help="File uploads will be implemented next.",
    )


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

if st.button("Start research", type="primary"):
    if question.strip():
        st.info(
            f"Question captured. Selected model: {model}. "
            "Agent integration comes next."
        )
    else:
        st.toast("Please enter a research question.", icon="⚠️")
