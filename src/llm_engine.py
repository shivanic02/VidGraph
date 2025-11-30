import json
import google.generativeai as genai
import re

def get_available_model():
    """Finds a valid Gemini model automatically based on your API key permissions."""
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name: return m.name
                if 'pro' in m.name and '1.5' in m.name: return m.name
        return "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

def extract_knowledge_graph(transcript, api_key):
    """Generates the Knowledge Graph nodes and edges."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(get_available_model())
        
        prompt = f"""
        You are a Knowledge Graph creator. Analyze the text and identify:
        1. "Core Concepts" (The main 3-5 topics).
        2. "Sub Concepts" (The details supporting them).
        
        Transcript: 
        {transcript[:30000]} 

        Output STRICTLY JSON (no markdown):
        {{
          "nodes": [
             {{"id": "Main Topic", "label": "Main Topic", "type": "core"}},
             {{"id": "Sub Detail", "label": "Sub Detail", "type": "sub"}}
          ],
          "edges": [
             {{"source": "Main Topic", "target": "Sub Detail", "label": "includes"}}
          ]
        }}
        """
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)

    except Exception as e:
        return {"error": f"Graph Error: {str(e)}"}

def generate_quiz(transcript, api_key):
    """Generates a 3-question quiz."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(get_available_model())
        
        prompt = f"""
        Generate 3 multiple-choice questions based on this text.
        
        Transcript:
        {transcript[:30000]}

        Output STRICTLY JSON (no markdown):
        [
            {{
                "question": "Question text here?",
                "options": ["Full text of Option A", "Full text of Option B", "Full text of Option C", "Full text of Option D"],
                "answer": "Full text of Option B",
                "explanation": "Brief explanation of why B is correct."
            }}
        ]
        
        IMPORTANT: The "answer" field must MATCH EXACTLY one of the strings in the "options" list.
        """
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)

    except Exception as e:
        return [{"error": str(e)}]

def generate_summary(transcript, api_key):
    """Generates a concise executive summary."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(get_available_model())
        
        prompt = f"""
        Write a high-level executive summary of the following transcript.
        Use bullet points for readability. Keep it under 250 words.
        
        Transcript:
        {transcript[:30000]}
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"Error generating summary: {str(e)}"