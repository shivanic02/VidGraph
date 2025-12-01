import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import google.generativeai as genai 
from gtts import gTTS # Audio Generation
import io

# Import engines
from src.llm_engine import extract_knowledge_graph, generate_quiz, generate_summary, get_available_model
from src.graph_builder import visualize_knowledge_graph
from src.pdf_generator import create_pdf

load_dotenv()

# --- APP CONFIGURATION ---
st.set_page_config(page_title="VidGraph.ai", layout="wide", page_icon="🧠")

# --- CUSTOM CSS: PREMIUM DARK THEME ---
st.markdown("""
<style>
    /* Dark Background */
    .stApp {
        background-color: #121212;
    }

    /* Text Colors - Force Light/White */
    h1, h2, h3, h4, h5, h6, p, li, span, div, label {
        color: #E0E0E0 !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1E1E1E;
        border-right: 1px solid #333;
    }
    
    /* Inputs */
    .stTextArea textarea {
        background-color: #2D2D2D !important;
        color: #E0E0E0 !important;
        border: 1px solid #444;
    }
    
    /* Gradient Buttons */
    div.stButton > button {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        color: #000 !important;
        font-weight: bold;
        border: none;
        padding: 10px 25px;
        border-radius: 8px;
        transition: transform 0.2s;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        color: #000 !important;
    }
    
    /* Tab Styling */
    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #E0E0E0 !important;
        font-weight: 600;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #00C9FF !important;
        border-bottom: 2px solid #00C9FF !important;
    }
    
    /* Chat Bubbles */
    .stChatMessage {
        background-color: #262730;
        border: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## ⚙️ Intelligence Hub")
    
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Neural Engine Active")
    else:
        api_key = st.text_input("Gemini API Key", type="password")

    st.divider()
    
    # --- PERSONA SELECTOR ---
    st.markdown("### 🎭 Tutor Persona")
    persona = st.selectbox(
        "Choose your learning style:",
        ["Standard", "👶 Explain Like I'm 5", "🧐 Academic / Expert"],
        index=0
    )
    
    st.divider()
    st.info("VidGraph transforms unstructured video data into interconnected knowledge maps.")

# --- MAIN CONTENT ---
st.title("VidGraph.ai 🧠")
st.markdown("#### The AI-Powered Knowledge Cartographer")

# --- INPUT SECTION ---
transcript_input = st.text_area(
    "📥 Knowledge Source", 
    height=200, 
    placeholder="Paste lecture transcript, video captions, or research notes here..."
)

col1, col2 = st.columns([1, 5])
with col1:
    generate_btn = st.button("🚀 Visualize", type="primary")

# --- LOGIC ---
if generate_btn:
    if not api_key:
        st.error("⚠️ System Offline: API Key Missing.")
    elif not transcript_input:
        st.warning("⚠️ Input Required: Please paste source text.")
    else:
        st.session_state['transcript'] = transcript_input
        st.session_state['persona'] = persona 
        
        with st.spinner("🔮 Mapping Neural Connections..."):
            # Pass the 'persona' to the AI functions
            graph_data = extract_knowledge_graph(transcript_input, api_key, persona)
            quiz_data = generate_quiz(transcript_input, api_key, persona)
            summary_text = generate_summary(transcript_input, api_key, persona)
            
            st.session_state['graph_data'] = graph_data
            st.session_state['quiz_data'] = quiz_data
            st.session_state['summary_text'] = summary_text
            st.session_state.messages = [] 
            
            st.rerun()

# --- RESULTS DASHBOARD ---
if 'graph_data' in st.session_state:
    
    st.markdown("---")
    
    # 4 TABS
    tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Knowledge Graph", "🎙️ Audio Brief", "📝 Quiz", "💬 AI Chat"])
    
    # TAB 1: GRAPH
    with tab1:
        st.subheader(f"Concept Map ({st.session_state.get('persona', 'Standard')})")
        if "error" in st.session_state['graph_data']:
            st.error(st.session_state['graph_data']['error'])
        else:
            html_graph = visualize_knowledge_graph(st.session_state['graph_data'])
            components.html(html_graph, height=600, scrolling=True)

    # TAB 2: AUDIO SUMMARY
    with tab2:
        st.subheader("🎧 Audio Overview")
        st.caption("Listen to the AI-generated summary of this topic.")
        
        summary = st.session_state.get('summary_text', "No summary available.")
        st.markdown(f"**Text Summary:**\n{summary}")
        
        if st.button("▶️ Generate Audio"):
            with st.spinner("Synthesizing voice..."):
                try:
                    tts = gTTS(text=summary, lang='en', slow=False)
                    mp3_fp = io.BytesIO()
                    tts.write_to_fp(mp3_fp)
                    st.audio(mp3_fp, format='audio/mp3')
                except Exception as e:
                    st.error(f"Audio generation failed: {e}")

    # TAB 3: QUIZ
    with tab3:
        st.subheader("✅ Knowledge Check")
        quiz_data = st.session_state.get('quiz_data')
        if not quiz_data or "error" in quiz_data:
            st.warning("Quiz unavailable.")
        else:
            for i, q in enumerate(quiz_data):
                with st.expander(f"Question {i+1}: {q['question']}", expanded=True):
                    user_answer = st.radio("Select Answer:", q['options'], key=f"q{i}")
                    if st.button("Submit", key=f"btn{i}"):
                        if user_answer.strip() == q['answer'].strip():
                            st.success(f"Correct! {q.get('explanation', '')}")
                        else:
                            st.error(f"Incorrect. The correct answer is: {q['answer']}")

    # TAB 4: CHAT
    with tab4:
        st.subheader("💬 Socratic Tutor")
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(get_available_model())
                    full_prompt = f"""
                    Context: {st.session_state['transcript'][:30000]}
                    Persona: {st.session_state.get('persona', 'Standard')}
                    Question: {prompt}
                    """
                    response = model.generate_content(full_prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- FOOTER ACTIONS ---
    st.markdown("---")
    col_a, col_b = st.columns([4, 1])
    with col_b:
        if st.button("📥 Download PDF Guide"):
            with st.spinner("Compiling..."):
                pdf_bytes = create_pdf(
                    st.session_state['summary_text'],
                    st.session_state['graph_data'],
                    st.session_state['quiz_data']
                )
                st.download_button("Download PDF", pdf_bytes, "VidGraph_Guide.pdf", "application/pdf")