import streamlit as st
from dotenv import load_dotenv
from src.llm_engine import extract_knowledge_graph

load_dotenv()

# --- MOCK DATA ---
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

st.set_page_config(page_title="VidGraph.ai", layout="wide")
st.markdown('<p style="font-size: 2.5rem; color: #4B4B4B;">VidGraph.ai 🧠</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Input Settings")
    video_url = st.text_input("YouTube URL", value="https://www.youtube.com/watch?v=OhCzX0iLnOc")
    
    # --- UPDATED LABEL FOR GEMINI ---
    api_key = st.text_input("Google Gemini API Key", type="password")
    
    st.caption("[Get a Free Gemini Key Here](https://aistudio.google.com/app/apikey)")

    if st.button("Generate Graph"):
        if not api_key:
            st.error("Please provide a Google API Key.")
        else:
            st.success("Transcript loaded (Mock Mode)")
            st.session_state['transcript'] = MOCK_TRANSCRIPT
            
            with st.spinner("Gemini is analyzing connections..."):
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
        st.json(st.session_state['graph_data'])
    else:
        st.info("Graph visualization will appear here.")

with col2:
    st.subheader("Transcript")
    if 'transcript' in st.session_state:
        st.write(st.session_state['transcript'])