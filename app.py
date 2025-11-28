import streamlit as st
import streamlit.components.v1 as components
import re
import os
from dotenv import load_dotenv

# Import custom modules
from src.llm_engine import extract_knowledge_graph
from src.graph_builder import visualize_knowledge_graph

# Try to import the YouTube library safely
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    YOUTUBE_LIB_AVAILABLE = True
except ImportError:
    YOUTUBE_LIB_AVAILABLE = False

load_dotenv()

# --- HELPER: Video ID Extractor ---
def get_video_id(url):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None

# --- HELPER: Transcript Fetcher ---
def get_transcript_safe(video_id):
    if not YOUTUBE_LIB_AVAILABLE:
        return None, "Library not installed"
    
    try:
        # Standard call
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([item['text'] for item in transcript_list])
        return full_text, None
    except Exception as e:
        # Catch the specific Attribute error or any other block
        return None, str(e)

# --- APP LAYOUT ---
st.set_page_config(page_title="VidGraph.ai", layout="wide")

# Custom Title
st.markdown('<h1 style="color: #4B4B4B;">VidGraph.ai 🧠</h1>', unsafe_allow_html=True)
st.caption("Transform YouTube Videos into Interactive Knowledge Graphs")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API Key Logic
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ API Key Loaded")
    else:
        api_key = st.text_input("Gemini API Key", type="password")
        st.caption("Tip: Use .streamlit/secrets.toml")

    st.divider()
    
    st.header("📺 Video Source")
    video_url = st.text_input("YouTube URL", value="https://www.youtube.com/watch?v=OhCzX0iLnOc")
    
    if st.button("🚀 Generate Graph", type="primary"):
        if not api_key:
            st.error("Missing API Key")
        elif not video_url:
            st.error("Missing URL")
        else:
            # RESET STATE
            st.session_state['transcript'] = None
            st.session_state['graph_data'] = None
            
            # 1. Try Auto-Fetch
            video_id = get_video_id(video_url)
            if video_id:
                with st.spinner("Fetching transcript..."):
                    text, error = get_transcript_safe(video_id)
                    
                    if text:
                        st.session_state['transcript'] = text
                        st.success("Transcript fetched!")
                    else:
                        st.warning("⚠️ Auto-fetch unavailable. Switching to Manual Mode.")
                        st.session_state['show_manual'] = True
            else:
                st.error("Invalid YouTube URL")

# --- MANUAL INPUT FALLBACK ---
if st.session_state.get('show_manual'):
    st.info("Paste the transcript below (Get it from the YouTube video description):")
    manual_text = st.text_area("Transcript Text", height=200)
    
    if st.button("Process Manual Text"):
        if manual_text:
            st.session_state['transcript'] = manual_text
            st.session_state['show_manual'] = False
            st.rerun()

# --- GRAPH GENERATION LOGIC ---
if st.session_state.get('transcript'):
    # Check if we need to run AI (don't re-run if we already have graph data)
    if not st.session_state.get('graph_data'):
        with st.spinner("🧠 Gemini is mapping connections..."):
            data = extract_knowledge_graph(st.session_state['transcript'], api_key)
            
            if "error" in data:
                st.error(data['error'])
            else:
                st.session_state['graph_data'] = data

# --- RESULTS DISPLAY ---
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Interactive Graph")
    if st.session_state.get('graph_data'):
        html = visualize_knowledge_graph(st.session_state['graph_data'])
        components.html(html, height=600, scrolling=True)
    else:
        st.markdown("*Graph will appear here...*")

with col2:
    st.subheader("Source Data")
    if st.session_state.get('transcript'):
        st.text_area("Read Transcript", st.session_state['transcript'], height=600)