import streamlit as st
import streamlit.components.v1 as components
import re
import os
from dotenv import load_dotenv

# --- SMART IMPORT ---
# We import the library, but we don't assume the command yet
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    YOUTUBE_LIB_AVAILABLE = True
except ImportError:
    YOUTUBE_LIB_AVAILABLE = False

from src.llm_engine import extract_knowledge_graph
from src.graph_builder import visualize_knowledge_graph

load_dotenv()

# --- HELPER FUNCTIONS ---
def get_video_id(url):
    """Extracts Video ID from URL"""
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_transcript_safe(video_id):
    """
    Universally fetches transcript regardless of library version.
    """
    if not YOUTUBE_LIB_AVAILABLE:
        return None, "Library not installed."

    try:
        # STRATEGY 1: The New v1.x Syntax (Instance Method)
        # Check if the 'fetch' method exists in the class directory
        if hasattr(YouTubeTranscriptApi, 'fetch'):
            # In the new version, we must instantiate the class first
            api = YouTubeTranscriptApi() 
            transcript_list = api.fetch(video_id)
            
            # The new version returns Objects, not Dictionaries
            # We check if the items have a '.text' attribute
            try:
                full_text = " ".join([item.text for item in transcript_list])
            except AttributeError:
                # Fallback if they are still dicts
                full_text = " ".join([item['text'] for item in transcript_list])
            
            return full_text, None

        # STRATEGY 2: The Old Static Syntax (Classic)
        elif hasattr(YouTubeTranscriptApi, 'get_transcript'):
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([item['text'] for item in transcript_list])
            return full_text, None
        
        else:
            return None, "Unknown library version (No fetch/get_transcript)."

    except Exception as e:
        return None, str(e)

# --- APP LAYOUT ---
st.set_page_config(page_title="VidGraph.ai", layout="wide")
st.markdown('<h1 style="color: #4B4B4B;">VidGraph.ai 🧠</h1>', unsafe_allow_html=True)
st.caption("Turn YouTube Videos into Knowledge Graphs")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Connected to Gemini")
    else:
        api_key = st.text_input("Gemini API Key", type="password")

    st.divider()
    st.header("📺 Video Source")
    video_url = st.text_input("YouTube URL", value="https://www.youtube.com/watch?v=OhCzX0iLnOc")
    
    if st.button("🚀 Generate Graph", type="primary"):
        if not api_key:
            st.error("Missing API Key")
        elif not video_url:
            st.error("Missing URL")
        else:
            # RESET
            st.session_state['transcript'] = None
            st.session_state['graph_data'] = None
            
            # FETCH
            video_id = get_video_id(video_url)
            if video_id:
                with st.spinner("Fetching transcript (Universal Mode)..."):
                    text, error = get_transcript_safe(video_id)
                    
                    if text:
                        st.session_state['transcript'] = text
                        st.success("Transcript fetched automatically!")
                    else:
                        st.error(f"Auto-fetch failed: {error}")
                        st.warning("Please try the Manual Paste mode if this persists.")
                        st.session_state['show_manual'] = True
            else:
                st.error("Invalid YouTube URL")

# --- MANUAL FALLBACK ---
if st.session_state.get('show_manual'):
    st.info("Paste the transcript below:")
    manual_text = st.text_area("Transcript Text", height=200)
    if st.button("Process Manual Text"):
        st.session_state['transcript'] = manual_text
        st.session_state['show_manual'] = False
        st.rerun()

# --- GRAPH GENERATION ---
if st.session_state.get('transcript'):
    if not st.session_state.get('graph_data'):
        with st.spinner("🧠 Gemini is mapping connections..."):
            data = extract_knowledge_graph(st.session_state['transcript'], api_key)
            if "error" in data:
                st.error(data['error'])
            else:
                st.session_state['graph_data'] = data

# --- VISUALIZATION ---
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Interactive Graph")
    if st.session_state.get('graph_data'):
        html = visualize_knowledge_graph(st.session_state['graph_data'])
        components.html(html, height=600, scrolling=True)
    else:
        st.info("Graph will appear here")

with col2:
    st.subheader("Source Data")
    if st.session_state.get('transcript'):
        st.text_area("Text", st.session_state['transcript'], height=600)