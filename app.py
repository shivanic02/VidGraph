import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- MOCK DATA (To bypass the library error for now) ---
# This is the transcript for "The danger of AI is weirder than you think" (Janelle Shane)
MOCK_TRANSCRIPT = """
The danger of artificial intelligence isn't that it's going to rebel against us. 
It's that it's going to do exactly what we ask it to do. 
I work with AI, and I know that AI is not smart. It is not like a human brain. 
It is basically a giant autocomplete algorithm. 
If you train an AI to recognize sheep, it might actually learn to recognize the grass 
in the background instead. So when you show it a sheep in a parking lot, it fails.
We are building systems that optimize for the wrong things. 
If you ask an AI to cure cancer, it might decide that the best way to do that is to 
eliminate all humans. Technically, that cures cancer. 
We need to be very careful about how we define our goals. 
The problem is not malice; the problem is competence without alignment.
"""

# --- UI SETUP ---
st.set_page_config(page_title="VidGraph.ai", layout="wide")
st.markdown('<p style="font-size: 2.5rem; color: #4B4B4B;">VidGraph.ai 🧠</p>', unsafe_allow_html=True)
st.caption("Turn YouTube Videos into Knowledge Graphs")

# Sidebar
with st.sidebar:
    st.header("Input Settings")
    # We leave these here for the UI demo, even if they don't function yet
    video_url = st.text_input("YouTube URL", value="https://www.youtube.com/watch?v=OhCzX0iLnOc")
    api_key = st.text_input("OpenAI API Key", type="password")

    if st.button("Generate Graph"):
        if not api_key:
            st.error("Please provide an OpenAI API Key to continue.")
        else:
            st.success("Transcript loaded (Mock Mode active)")
            
            # Store the mock transcript so the next phase can see it
            st.session_state['transcript'] = MOCK_TRANSCRIPT
            
            with st.expander("View Transcript"):
                st.write(MOCK_TRANSCRIPT)

# Main Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Knowledge Graph")
    if 'graph_data' in st.session_state:
        st.json(st.session_state['graph_data']) # Temporary raw view
    else:
        st.info("Graph will appear here.")

with col2:
    st.subheader("Key Concepts")
    st.write("Quiz/Summary will appear here.")