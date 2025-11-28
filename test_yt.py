from youtube_transcript_api import YouTubeTranscriptApi

print("Attempting to fetch transcript...")
try:
    # We test with the video ID "OhCzX0iLnOc"
    data = YouTubeTranscriptApi.get_transcript("OhCzX0iLnOc")
    print("SUCCESS! I found", len(data), "lines of text.")
except Exception as e:
    print("FAILURE:", e)