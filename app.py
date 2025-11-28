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
        if not video_url or not api_key:
            st.error("Please provide both a URL and an API Key.")
        else:
            with st.spinner("Processing video..."):
                # Placeholder for future logic
                st.success(f"Processing video: {video_url}")
                st.info("Backend logic coming in Phase 2!")

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