import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from rag.rag_assistant import OperationsHandbookRAG

st.set_page_config(
    page_title="GSE Operations Assistant",
    page_icon="📚",
    layout="wide"
)

@st.cache_resource
def load_rag_assistant():
    handbook_path = Path(__file__).parent.parent / "docs" / "OPERATIONS_HANDBOOK.md"
    rag = OperationsHandbookRAG(str(handbook_path))
    rag.build_index()
    return rag

st.title("📚 GSE Operations Handbook Assistant")
st.markdown("Ask questions about GSE operations, procedures, troubleshooting, and maintenance.")

try:
    rag = load_rag_assistant()
    
    st.sidebar.header("Quick Questions")
    quick_questions = [
        "How do I perform an emergency shutdown of the GPU?",
        "What is the startup procedure for the cryogenic line?",
        "How do I troubleshoot low voltage on the GPU?",
        "What should I do if the cryo valve won't open?",
        "What are the maintenance requirements for the GPU?",
        "How do I respond to a cryogenic leak?",
        "What is the normal shutdown procedure for the GPU?",
        "What are the operating limits for the cryogenic line?"
    ]
    
    selected_question = st.sidebar.radio("Select a quick question:", ["Custom"] + quick_questions)
    
    if selected_question == "Custom":
        question = st.text_input("Enter your question:", placeholder="e.g., How do I start the ground power unit?")
    else:
        question = selected_question
        st.info(f"Selected question: {question}")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    with col2:
        top_k = st.slider("Number of sources to retrieve:", 1, 10, 3)
    
    if search_button and question:
        with st.spinner("Searching operations handbook..."):
            result = rag.answer_question(question, top_k=top_k)
        
        st.success("Answer found!")
        
        st.subheader("📝 Answer")
        st.markdown(result['answer'])
        
        st.subheader("📚 Sources")
        for i, source in enumerate(result['sources'], 1):
            with st.expander(f"Source {i}: {source['section']} > {source['subsection']} (Relevance: {source['relevance_score']:.2%})"):
                context_lines = result['context'].split('\n\n---\n\n')
                if i - 1 < len(context_lines):
                    st.markdown(context_lines[i - 1])
        
        st.divider()
        
        with st.expander("🔍 View Full Context"):
            st.text(result['context'])
    
    st.sidebar.divider()
    st.sidebar.header("About")
    st.sidebar.info(
        "This RAG (Retrieval-Augmented Generation) assistant uses semantic search "
        "to find relevant information from the GSE Operations Handbook. "
        "\n\nIt can help with:\n"
        "- Standard Operating Procedures\n"
        "- Emergency procedures\n"
        "- Troubleshooting guides\n"
        "- Maintenance schedules\n"
        "- Safety information"
    )
    
    st.sidebar.header("Tips")
    st.sidebar.markdown(
        "- Be specific in your questions\n"
        "- Include device names (GPU, CRYO)\n"
        "- Mention the type of procedure (startup, shutdown, emergency)\n"
        "- Ask about specific problems or symptoms"
    )

except Exception as e:
    st.error(f"Error loading RAG assistant: {str(e)}")
    st.info("Make sure the operations handbook exists at docs/OPERATIONS_HANDBOOK.md")
    
    if st.button("Show Error Details"):
        st.exception(e)
