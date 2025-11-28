import json
import google.generativeai as genai
import re

def get_available_model():
    """Finds a valid Gemini model automatically."""
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name: return m.name
                if 'pro' in m.name and '1.5' in m.name: return m.name
        return "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

def extract_knowledge_graph(transcript, api_key):
    """Sends text to Gemini and requests JSON."""
    try:
        genai.configure(api_key=api_key)
        model_name = get_available_model()
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        You are a Knowledge Graph creator. 
        Analyze the transcript and extract key concepts and relationships.
        
        Transcript: 
        {transcript[:30000]} 

        Output STRICTLY a JSON object. No markdown.
        {{
          "nodes": [
             {{"id": "Concept1", "label": "Concept1", "color": "#4F46E5"}},
             {{"id": "Concept2", "label": "Concept2", "color": "#4F46E5"}}
          ],
          "edges": [
             {{"source": "Concept1", "target": "Concept2", "label": "relates to"}}
          ]
        }}
        """
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)

    except Exception as e:
        return {"error": f"Model {model_name} failed: {str(e)}"}