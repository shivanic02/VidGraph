from src.extractor import get_video_id, get_transcript

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Configuration
st.set_page_config(page_title="VidGraph.ai", layout="wide")

# Custom CSS for a better look
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .main-header {
        font-size: 2.5rem;
        color: #4B4B4B;
    }
</style>
""", unsafe_allow_html=True)

# Main Title
st.markdown('<p class="main-header">VidGraph.ai 🧠</p>', unsafe_allow_html=True)
st.caption("Turn YouTube Videos into Knowledge Graphs")

# Sidebar for Inputs
with st.sidebar:
    st.header("Input Settings")
    video_url = st.text_input("YouTube URL", placeholder="https://youtube.com/...")
    api_key = st.text_input("OpenAI API Key", type="password")

    if st.button("Generate Graph"):
        if not video_url:
            st.error("Please provide a URL.")
        else:
            with st.spinner("Fetching transcript..."):
                # 1. Extract Video ID
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
                        # Debugging: Show the first 500 characters to prove it works
                        with st.expander("View Raw Transcript"):
                            st.write(transcript_text[:500] + "...")

                        # Store in session state for the next step
                        st.session_state['transcript'] = transcript_text

# Main Content Area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Knowledge Graph")
    # Placeholder for the graph
    st.write("Graph will appear here.")

with col2:
    st.subheader("Key Concepts")
    # Placeholder for the quiz/summary
    st.write("Summary/Quiz will appear here.")