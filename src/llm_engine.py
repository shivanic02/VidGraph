import json
import google.generativeai as genai
import re

def extract_knowledge_graph(transcript, api_key):
    """
    Sends text to Gemini Pro and requests a Knowledge Graph (Nodes/Edges).
    """
    try:
        # 1. Configure the API
        genai.configure(api_key=api_key)
        
        # 2. Select the Stable Model (gemini-pro is universally available)
        model = genai.GenerativeModel('gemini-pro')
        
        # 3. Define the Prompt (Stronger JSON enforcement)
        prompt = f"""
        You are a Knowledge Graph creator. 
        Analyze the following transcript and extract key concepts and their relationships.
        
        Transcript: 
        {transcript[:30000]} 

        Output STRICTLY a JSON object with this structure. Do not add markdown ```json blocks. Just the raw string:
        {{
          "nodes": [
             {{"id": "Concept1", "label": "Concept1", "color": "#4F46E5"}},
             {{"id": "Concept2", "label": "Concept2", "color": "#4F46E5"}}
          ],
          "edges": [
             {{"source": "Concept1", "target": "Concept2", "label": "relates to"}}
          ]
        }}
        
        Rules:
        1. Identify 8-15 key concepts.
        2. Connect them logically.
        3. Keep labels short (1-3 words).
        """

        # 4. Generate Content (Standard Mode)
        response = model.generate_content(prompt)
        
        # 5. Clean the response (Gemini sometimes adds ```json at the start)
        raw_text = response.text
        # Remove markdown code blocks if present
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        
        # 6. Parse JSON
        result = json.loads(clean_text)
        return result

    except Exception as e:
        return {"error": str(e)}