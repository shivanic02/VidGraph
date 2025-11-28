import re
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_id(url):
    """
    Extracts the video ID from a YouTube URL.
    Examples:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    """
    # Regex for extracting the video ID
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    
    if match:
        return match.group(1)
    return None

def get_transcript(video_id):
    """
    Fetches the transcript for a given video ID.
    Returns a single string containing the full text.
    """
    try:
        # Fetch the transcript (returns a list of dicts)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine all text parts into one large string
        full_text = " ".join([item['text'] for item in transcript_list])
        return full_text
        
    except Exception as e:
        return f"Error: Could not retrieve transcript. Reason: {str(e)}"