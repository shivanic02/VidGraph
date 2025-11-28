import json
import google.generativeai as genai

def extract_knowledge_graph(transcript, api_key):
    """
    Sends text to Gemini Flash and requests a Knowledge Graph (Nodes/Edges).
    """
    try:
        # 1. Configure the API
        genai.configure(api_key=AIzaSyAx7lk64cRh_kFaYpjm0KMPkxeVyX_y5JA)
        
        # 2. Select the Model (Flash is fast and free-tier eligible)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 3. Define the Prompt
        prompt = f"""
        You are a Knowledge Graph creator. 
        Analyze the following transcript and extract key concepts and their relationships.
        
        Transcript: 
        {transcript[:30000]} 

        Output STRICTLY a JSON object with this structure:
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

        # 4. Generate Content (Force JSON mode)
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # 5. Parse JSON
        result = json.loads(response.text)
        return result

    except Exception as e:
        return {"error": str(e)}