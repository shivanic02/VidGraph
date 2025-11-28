import streamlit as st
import streamlit.components.v1 as components
import os
import re
from dotenv import load_dotenv
import youtube_transcript_api
from src.llm_engine import extract_knowledge_graph
from src.graph_builder import visualize_knowledge_graph

# Load environment variables
load_dotenv()

# --- HELPER FUNCTIONS ---
def get_video_id(url):
    """Extracts Video ID from URL"""
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None


def get_transcript_safe(video_id):
    try:
        # We access the class THROUGH the module to stop Python getting confused
        transcript_list = youtube_transcript_api.YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([item['text'] for item in transcript_list])
        return full_text, None
    except Exception as e:
        return None, str(e)

# --- UI SETUP ---
st.set_page_config(page_title="VidGraph.ai", layout="wide")
st.markdown('<p style="font-size: 2.5rem; color: #4B4B4B;">VidGraph.ai 🧠</p>', unsafe_allow_html=True)
st.caption("Turn YouTube Videos into Knowledge Graphs")

# --- SIDEBAR & INPUTS ---
with st.sidebar:
    st.header("1. Settings")
    
    # API Key Loading
    if "GOOGLE_API_KEY" in st.secrets:
        default_key = st.secrets["GOOGLE_API_KEY"]
        api_key = st.text_input("Gemini API Key", value=default_key, type="password")
        st.success("Key loaded securely! 🔒")
    else:
        api_key = st.text_input("Gemini API Key", type="password")
        st.info("Tip: Add secrets.toml to auto-load this.")

    st.header("2. Video Source")
    # Default to a known working video for demo purposes
    video_url = st.text_input("YouTube URL", value="https://www.youtube.com/watch?v=OhCzX0iLnOc")
    
    # Initialize session state for manual entry if needed
    if 'manual_transcript' not in st.session_state:
        st.session_state['manual_transcript'] = ""

    if st.button("Generate Graph"):
        if not api_key:
            st.error("Please provide an API Key.")
        elif not video_url:
            st.error("Please provide a Video URL.")
        else:
            # 1. Extract Video ID
            video_id = get_video_id(video_url)
            
            if not video_id:
                st.error("Invalid YouTube URL.")
            else:
                with st.spinner("Fetching transcript..."):
                    # 2. Try Auto-Fetch
                    text, error = get_transcript_safe(video_id)
                    
                    if text:
                        # SUCCESS: We got it automatically
                        st.session_state['transcript'] = text
                        st.success("Transcript fetched automatically!")
                    else:
                        # FAILURE: Show error and ask for manual paste
                        st.warning(f"Auto-fetch failed ({error}). Switching to Manual Mode.")
                        st.session_state['transcript'] = None # Reset
                        st.session_state['show_manual_input'] = True

# --- MANUAL FALLBACK INPUT ---
if st.session_state.get('show_manual_input'):
    st.warning("⚠️ YouTube blocked the automated tool. Please paste the transcript below:")
    st.markdown(f"[Click here to open Transcript for this video]({video_url})")
    
    manual_text = st.text_area("Paste Transcript Here", height=300)
    
    if st.button("Process Manual Transcript"):
        if manual_text:
            st.session_state['transcript'] = manual_text
            st.session_state['show_manual_input'] = False
            st.rerun()

# --- MAIN LOGIC ---
if 'transcript' in st.session_state and st.session_state['transcript']:
    
    # Only run AI if we haven't already generated the graph for this specific text
    if 'current_processed_text' not in st.session_state or st.session_state['current_processed_text'] != st.session_state['transcript']:
        
        with st.spinner("Gemini is analyzing connections..."):
            graph_data = extract_knowledge_graph(st.session_state['transcript'], api_key)
            
            if "error" in graph_data:
                st.error(f"AI Error: {graph_data['error']}")
            else:
                st.session_state['graph_data'] = graph_data
                # Mark this text as processed so we don't re-run AI on refresh
                st.session_state['current_processed_text'] = st.session_state['transcript']

# --- DISPLAY RESULTS ---
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Knowledge Graph")
    if 'graph_data' in st.session_state:
        html_graph = visualize_knowledge_graph(st.session_state['graph_data'])
        components.html(html_graph, height=600, scrolling=True)
    else:
        st.info("Graph will appear here.")

with col2:
    st.subheader("Transcript")
    if 'transcript' in st.session_state:
        st.text_area("Source Text", st.session_state['transcript'], height=600)