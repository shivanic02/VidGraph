import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- HELPER FUNCTIONS (Moved here to fix import error) ---

def get_video_id(url):
    """Extracts Video ID from URL"""
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

def get_transcript(video_id):
    """Fetches transcript using the library"""
    try:
        # Direct call to the library
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Join text
        full_text = " ".join([item['text'] for item in transcript_list])
        return full_text
    except Exception as e:
        # Return the specific error message
        return f"Error: {str(e)}"

# --- MAIN APP UI ---

st.set_page_config(page_title="VidGraph.ai", layout="wide")
st.markdown('<p style="font-size: 2.5rem; color: #4B4B4B;">VidGraph.ai 🧠</p>', unsafe_allow_html=True)
st.caption("Turn YouTube Videos into Knowledge Graphs")

# Sidebar
with st.sidebar:
    st.header("Input Settings")
    video_url = st.text_input("YouTube URL", placeholder="https://youtube.com/...")
    api_key = st.text_input("OpenAI API Key", type="password")

    if st.button("Generate Graph"):
        if not video_url:
            st.error("Please provide a URL.")
        else:
            with st.spinner("Fetching transcript..."):
                # 1. Extract ID
                video_id = get_video_id(video_url)
                
                if not video_id:
                    st.error("Invalid YouTube URL.")
                else:
                    # 2. Get Transcript
                    transcript_text = get_transcript(video_id)
                    
                    if "Error:" in transcript_text:
                        st.error(transcript_text)
                    else:
                        st.success("Transcript extracted successfully!")
                        st.session_state['transcript'] = transcript_text
                        
                        # Debug View
                        with st.expander("View Transcript Start"):
                            st.write(transcript_text[:500])

# Layout
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Knowledge Graph")
    st.info("Graph will appear here after API key integration.")

with col2:
    st.subheader("Key Concepts")