import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# Import our new engines
from src.llm_engine import extract_knowledge_graph, generate_quiz, generate_summary
from src.graph_builder import visualize_knowledge_graph

load_dotenv()

# --- APP CONFIGURATION ---
st.set_page_config(page_title="VidGraph.ai", layout="wide", page_icon="🧠")

st.markdown("""
<style>
    .stTextArea textarea { font-size: 14px; }
    div[data-testid="stExpander"] details summary { font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Gemini Key Loaded")
    else:
        api_key = st.text_input("Gemini API Key", type="password")

    st.divider()
    st.markdown("### ℹ️ How to use")
    st.info("Paste any text/transcript to generate a Knowledge Graph and a Practice Quiz.")

# --- MAIN HEADER ---
st.markdown('<h1 style="color: #4B4B4B;">VidGraph.ai 🧠</h1>', unsafe_allow_html=True)
st.caption("Advanced Learning Companion: Knowledge Graphs + AI Quizzes")

# --- INPUT SECTION ---
transcript_input = st.text_area("Paste Transcript / Text:", height=150)
generate_btn = st.button("🚀 Analyze & Generate", type="primary")

# --- PROCESSING LOGIC ---
if generate_btn:
    if not api_key:
        st.error("⚠️ Please enter a Google API Key.")
    elif not transcript_input:
        st.error("⚠️ Please paste text first.")
    else:
        st.session_state['transcript'] = transcript_input
        
        with st.spinner("🧠 Gemini is analyzing (Graph, Quiz, and Summary)..."):
            # 1. Generate Graph
            graph_data = extract_knowledge_graph(transcript_input, api_key)
            
            # 2. Generate Quiz
            quiz_data = generate_quiz(transcript_input, api_key)
            
            # 3. Generate Summary (NEW)
            summary_text = generate_summary(transcript_input, api_key)
            
            # Save all to session state
            st.session_state['graph_data'] = graph_data
            st.session_state['quiz_data'] = quiz_data
            st.session_state['summary_text'] = summary_text # Store it
            
            st.success("Analysis Complete!")

# --- RESULTS DISPLAY ---
if 'graph_data' in st.session_state:
    
    # Create Tabs for cleaner UI
    tab1, tab2 = st.tabs(["📊 Knowledge Graph", "📝 Practice Quiz"])
    
    # TAB 1: THE GRAPH
    with tab1:
        st.subheader("Interactive Concept Map")
        st.caption("🟡 Gold = Core Concepts | 🔵 Blue = Sub-concepts")
        
        if "error" in st.session_state['graph_data']:
            st.error(st.session_state['graph_data']['error'])
        else:
            html_graph = visualize_knowledge_graph(st.session_state['graph_data'])
            components.html(html_graph, height=600, scrolling=True)

    # TAB 2: THE QUIZ
    with tab2:
        st.subheader("Test Your Knowledge")
        quiz_data = st.session_state.get('quiz_data')
        
        if not quiz_data or "error" in quiz_data:
            st.error("Could not generate quiz.")
        else:
            # Loop through questions
            for i, q in enumerate(quiz_data):
                st.markdown(f"**Q{i+1}: {q['question']}**")
                
                # Radio button for options
                user_answer = st.radio(f"Select an answer for Q{i+1}:", q['options'], key=f"q{i}")
                
                # Check Answer Button (per question)
                if st.button(f"Check Answer {i+1}", key=f"btn{i}"):
                    # FIX: We clean both strings to remove invisible spaces
                    clean_user_answer = user_answer.strip()
                    clean_correct_answer = q['answer'].strip()
                    
                    if clean_user_answer == clean_correct_answer:
                        st.success(f"✅ Correct! {q.get('explanation', '')}")
                    else:
                        st.error(f"❌ Incorrect. The correct answer is: {q['answer']}")
                st.divider()

from src.pdf_generator import create_pdf

# ... (Previous code)

if 'quiz_data' in st.session_state:
    st.divider()
    st.subheader("3. Export Study Guide")
    
    if st.button("📥 Download PDF Report"):
        with st.spinner("Compiling PDF..."):
            pdf_bytes = create_pdf(
                st.session_state['summary_text'], # Pass the smart summary here!
                st.session_state['graph_data'],
                st.session_state['quiz_data']
            )
            
            st.download_button(
                label="📄 Download PDF",
                data=pdf_bytes,
                file_name="VidGraph_Study_Guide.pdf",
                mime="application/pdf"
            )