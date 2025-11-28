import re
# We use a direct import alias to avoid namespace confusion
from youtube_transcript_api import YouTubeTranscriptApi as YTApi

def get_video_id(url):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

def get_transcript(video_id):
    try:
        # Debug print to your terminal (check your black screen terminal)
        print(f"Attempting to fetch transcript for: {video_id}")
        
        # Use the aliased class
        transcript_list = YTApi.get_transcript(video_id)
        
        full_text = " ".join([item['text'] for item in transcript_list])
        print("Success! Transcript length:", len(full_text))
        return full_text
        
    except Exception as e:
        print(f"FAILED: {e}")
        return f"Error: {str(e)}"