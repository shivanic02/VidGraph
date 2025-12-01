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

def get_persona_instruction(persona):
    """Returns the system instruction based on the selected persona."""
    # --- UPDATED LOGIC FOR NEW NAMES ---
    if "Beginner" in persona:
        return "Explain simply, use analogies, avoid jargon. Keep it fun and easy to understand."
    elif "Expert" in persona:
        return "Use precise technical terminology, focus on depth, nuance, and advanced concepts. Be formal."
    else: # Standard
        return "Be clear, concise, and professional."

def extract_knowledge_graph(transcript, api_key, persona="Standard"):
    """Generates the Knowledge Graph with Node Importance."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(get_available_model())
        
        style = get_persona_instruction(persona)
        
        prompt = f"""
        You are a Knowledge Graph creator. 
        Style Requirement: {style}
        
        Analyze the text and identify:
        1. "Core Concepts" (The main 3-5 topics).
        2. "Sub Concepts" (The details supporting them).
        3. "Relationships" (Connect concepts logically).
        
        CRITICAL RULE: Ensure the graph is INTERCONNECTED. 
        - Find connections between different Core Concepts.
        - Find connections between Sub Concepts of different parents.
        - Do not create isolated clusters.
        
        Transcript: 
        {transcript[:30000]} 

        Output STRICTLY JSON (no markdown):
        {{
          "nodes": [
             {{"id": "Concept A", "label": "Concept A", "type": "core"}},
             {{"id": "Concept B", "label": "Concept B", "type": "sub"}}
          ],
          "edges": [
             {{"source": "Concept A", "target": "Concept B", "label": "includes"}},
             {{"source": "Concept B", "target": "Concept C", "label": "relates to"}}
          ]
        }}
        """
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)

    except Exception as e:
        return {"error": f"Graph Error: {str(e)}"}

def generate_quiz(transcript, api_key, persona="Standard"):
    """Generates a 3-question quiz."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(get_available_model())
        
        style = get_persona_instruction(persona)
        
        prompt = f"""
        Generate 3 multiple-choice questions based on this text.
        Style Requirement: {style}
        
        Transcript:
        {transcript[:30000]}

        Output STRICTLY JSON (no markdown):
        [
            {{
                "question": "Question text here?",
                "options": ["Full text of Option A", "Full text of Option B", "Full text of Option C", "Full text of Option D"],
                "answer": "Full text of Option B",
                "explanation": "Brief explanation."
            }}
        ]
        
        IMPORTANT: The "answer" field must MATCH EXACTLY one of the strings in the "options" list.
        """
        response = model.generate_content(prompt)
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)

    except Exception as e:
        return [{"error": str(e)}]

def generate_summary(transcript, api_key, persona="Standard"):
    """Generates a concise executive summary."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(get_available_model())
        
        style = get_persona_instruction(persona)
        
        prompt = f"""
        Write a high-level executive summary of the following transcript.
        Style Requirement: {style}
        Use bullet points for readability. Keep it under 250 words.
        
        Transcript:
        {transcript[:30000]}
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        return f"Error generating summary: {str(e)}"