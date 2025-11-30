import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import google.generativeai as genai 

# Import engines
from src.llm_engine import extract_knowledge_graph, generate_quiz, generate_summary, get_available_model
from src.graph_builder import visualize_knowledge_graph
from src.pdf_generator import create_pdf

load_dotenv()

# --- APP CONFIGURATION ---
st.set_page_config(page_title="VidGraph.ai", layout="wide", page_icon="🧠")

# --- CUSTOM CSS: THE "LIVELY" THEME (FIXED CONTRAST) ---
st.markdown("""
<style>
    /* 1. Force the background to a greish color */
    .stApp {
        background-color: #e8e8e8;
    }

    /* 2. CRITICAL FIX: Force all text to be dark gray/black */
    h1, h2, h3, h4, h5, h6, p, li, span, div, label {
        color: #2D3436 !important;
    }
    
    /* 3. Make the Sidebar distinct but readable */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
    
    /* 4. Text Areas: Clean White Cards with Dark Text */
    .stTextArea textarea {
        font-size: 16px;
        color: #2D3436 !important;
        background-color: #ffffff !important;
        border: 2px solid #dfe6e9;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* 5. Buttons: Gradient Pop */
    div.stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #FF8E53);
        color: white !important; /* Keep button text white */
        font-weight: bold;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
    }
    
    /* 6. Tabs styling */
    button[data-baseweb="tab"] {
        color: #2D3436 !important;
        font-weight: 600;
    }
    
    /* 7. Chat Bubbles Fix */
    .stChatMessage {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Connected")
    else:
        api_key = st.text_input("Gemini API Key", type="password")

    st.markdown("---")
    st.markdown("### 🌟 About")
    st.info("VidGraph turns dense text into living knowledge maps.")

# --- MAIN CONTENT ---
st.title("VidGraph.ai")
st.markdown("### 🧠 The AI Study Companion")
st.caption("Paste a transcript below to generate a Knowledge Graph, Quiz, and Study Guide.")

# --- INPUT SECTION ---
transcript_input = st.text_area(
    "📥 Input Source", 
    height=200, 
    placeholder="Paste your video transcript, lecture notes, or article here..."
)

col1, col2 = st.columns([1, 5])
with col1:
    generate_btn = st.button("✨ Generate", type="primary")

# --- PROCESSING LOGIC ---
if generate_btn:
    if not api_key:
        st.error("⚠️ Please enter a Google API Key in the sidebar.")
    elif not transcript_input:
        st.warning("⚠️ Please paste some text first.")
    else:
        st.session_state['transcript'] = transcript_input
        
        with st.spinner("🤖 AI is analyzing concepts..."):
            # Parallel Execution
            graph_data = extract_knowledge_graph(transcript_input, api_key)
            quiz_data = generate_quiz(transcript_input, api_key)
            summary_text = generate_summary(transcript_input, api_key)
            
            st.session_state['graph_data'] = graph_data
            st.session_state['quiz_data'] = quiz_data
            st.session_state['summary_text'] = summary_text
            st.session_state.messages = [] # Reset chat
            
            st.rerun() # Force refresh to show results

# --- RESULTS DISPLAY ---
if 'graph_data' in st.session_state:
    
    st.markdown("---")
    
    # TABS INTERFACE
    tab1, tab2, tab3 = st.tabs(["🗺️ Concept Map", "📝 Quiz", "💬 AI Chat"])
    
    with tab1:
        st.subheader("Interactive Knowledge Graph")
        if "error" in st.session_state['graph_data']:
            st.error(st.session_state['graph_data']['error'])
        else:
            # Render the updated colorful graph
            html_graph = visualize_knowledge_graph(st.session_state['graph_data'])
            components.html(html_graph, height=600, scrolling=True)
            st.caption("Tip: Click 'Fullscreen' inside the graph for a better view.")

    with tab2:
        st.subheader("✅ Practice Quiz")
        quiz_data = st.session_state.get('quiz_data')
        if not quiz_data or "error" in quiz_data:
            st.warning("Quiz generation failed. Try a longer text.")
        else:
            for i, q in enumerate(quiz_data):
                with st.expander(f"Question {i+1}: {q['question']}", expanded=True):
                    user_answer = st.radio("Choose answer:", q['options'], key=f"q{i}")
                    if st.button("Check", key=f"btn{i}"):
                        if user_answer.strip() == q['answer'].strip():
                            st.success(f"Correct! {q.get('explanation', '')}")
                        else:
                            st.error(f"Wrong. Correct: {q['answer']}")

    with tab3:
        st.subheader("💬 Chat with Document")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask about the transcript..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(get_available_model())
                    full_prompt = f"Context: {st.session_state['transcript'][:30000]}\n\nQuestion: {prompt}"
                    response = model.generate_content(full_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- EXPORT SECTION ---
    st.markdown("---")
    col_a, col_b = st.columns([4, 1])
    with col_b:
        if st.button("📥 Export PDF"):
            with st.spinner("Generating PDF..."):
                pdf_bytes = create_pdf(
                    st.session_state['summary_text'],
                    st.session_state['graph_data'],
                    st.session_state['quiz_data']
                )
                st.download_button("Click to Download", pdf_bytes, "VidGraph_Study_Guide.pdf", "application/pdf")