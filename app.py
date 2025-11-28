import streamlit as st
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv

# We no longer need the YouTube library!
from src.llm_engine import extract_knowledge_graph
from src.graph_builder import visualize_knowledge_graph

load_dotenv()

# --- APP CONFIGURATION ---
st.set_page_config(page_title="VidGraph.ai", layout="wide", page_icon="🧠")

# --- CSS FOR BETTER UI ---
st.markdown("""
<style>
    .stTextArea textarea {
        font-size: 14px; 
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    
    # 1. API Key Logic
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ Gemini Key Loaded")
    else:
        api_key = st.text_input("Gemini API Key", type="password")
        st.caption("Get a free key from Google AI Studio")

    st.divider()
    
    st.markdown("### ℹ️ How it works")
    st.markdown("""
    1. Copy transcript from a YouTube video (or any text).
    2. Paste it into the box.
    3. Click **Generate Graph**.
    4. Explore the connections!
    """)
    
    st.divider()
    st.markdown("Built for **CodeCraze 2025**")

# --- MAIN CONTENT ---
st.markdown('<h1 style="color: #4B4B4B;">VidGraph.ai 🧠</h1>', unsafe_allow_html=True)
st.caption("Transform raw text into interactive Knowledge Graphs using Google Gemini.")

# 1. INPUT SECTION
st.subheader("1. Input Source")
transcript_input = st.text_area(
    "Paste your video transcript or article text here:",
    height=200,
    placeholder="Example: Machine learning is a field of inquiry devoted to understanding and building methods that 'learn'..."
)

# 2. ACTION BUTTON
generate_btn = st.button("🚀 Generate Knowledge Graph", type="primary")

# 3. LOGIC & VISUALIZATION
if generate_btn:
    if not api_key:
        st.error("⚠️ Please enter a Google API Key in the sidebar.")
    elif not transcript_input:
        st.error("⚠️ Please paste some text first.")
    else:
        # Save to session state so it doesn't vanish on refresh
        st.session_state['transcript'] = transcript_input
        
        with st.spinner("🧠 Gemini is analyzing concepts and connections..."):
            # Call the AI Engine
            data = extract_knowledge_graph(transcript_input, api_key)
            
            if "error" in data:
                st.error(f"AI Error: {data['error']}")
            else:
                st.session_state['graph_data'] = data
                st.success("Graph generated successfully!")

# 4. RESULTS DISPLAY
if 'graph_data' in st.session_state:
    st.divider()
    st.subheader("2. Interactive Graph")
    
    # Render the graph
    html_graph = visualize_knowledge_graph(st.session_state['graph_data'])
    components.html(html_graph, height=600, scrolling=True)
    
    # Optional: Show the raw data in an expander for debugging
    with st.expander("View Graph Data (JSON)"):
        st.json(st.session_state['graph_data'])