import streamlit as st
import os
from dotenv import load_dotenv
from src.llm_engine import extract_knowledge_graph

# Load environment variables (this reads your .env file)
load_dotenv()

# --- MOCK DATA ---
# (We use this temporarily to bypass the YouTube library error)
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
The problem is not malice; the problem is competence without alignment.
"""

# --- UI SETUP ---
st.set_page_config(page_title="VidGraph.ai", layout="wide")
st.markdown('<p style="font-size: 2.5rem; color: #4B4B4B;">VidGraph.ai 🧠</p>', unsafe_allow_html=True)
st.caption("Turn YouTube Videos into Knowledge Graphs")

# Sidebar
with st.sidebar:
    st.header("Input Settings")
    video_url = st.text_input("YouTube URL", value="https://www.youtube.com/watch?v=OhCzX0iLnOc")
    
    # --- AUTO-LOAD KEY ---
    # We try to get the key from the .env file. If not found, it's blank.
    env_key = os.getenv("GOOGLE_API_KEY")
    api_key = st.text_input("Google Gemini API Key", value=env_key, type="password")
    
    if not api_key:
        st.warning("⚠️ No API Key found. Check your .env file or paste one manually.")
        st.markdown("[Get a Free Gemini Key](https://aistudio.google.com/app/apikey)")

    if st.button("Generate Graph"):
        if not api_key:
            st.error("Please provide a Google API Key.")
        else:
            st.success("Transcript loaded (Mock Mode)")
            st.session_state['transcript'] = MOCK_TRANSCRIPT
            
            with st.spinner("Gemini is analyzing connections..."):
                # Call the Brain
                graph_data = extract_knowledge_graph(MOCK_TRANSCRIPT, api_key)
                
                if "error" in graph_data:
                    st.error(f"AI Error: {graph_data['error']}")
                else:
                    st.success("Graph Generated Successfully!")
                    st.session_state['graph_data'] = graph_data

# Main Layout
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Knowledge Graph")
    if 'graph_data' in st.session_state:
        # TEMP: Show raw JSON to prove it works
        st.json(st.session_state['graph_data'])
    else:
        st.info("Graph visualization will appear here.")

with col2:
    st.subheader("Transcript")
    if 'transcript' in st.session_state:
        st.text_area("Read Transcript", st.session_state['transcript'], height=400)