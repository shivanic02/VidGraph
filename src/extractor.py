import re
import youtube_transcript_api # Import the whole module, not just the class

def get_video_id(url):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

def get_transcript(video_id):
    try:
        # Access the class explicitly through the module
        transcript_list = youtube_transcript_api.YouTubeTranscriptApi.get_transcript(video_id)
        
        full_text = " ".join([item['text'] for item in transcript_list])
        return full_text
        
    except Exception as e:
        return f"Error: Could not retrieve transcript. Reason: {str(e)}"