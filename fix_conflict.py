import os
import sys

print("--- DIAGNOSTIC START ---")

try:
    # 1. Import the library causing issues
    import youtube_transcript_api
    
    # 2. Get its location on your computer
    location = youtube_transcript_api.__file__
    print(f"FOUND LIBRARY AT: {location}")
    
    # 3. Check if it's the real library or a fake local file
    if "site-packages" in location or "dist-packages" in location:
        print("✅ GOOD NEWS: You are loading the real installed library.")
        print("If it still fails, try: pip install --upgrade youtube-transcript-api")
    else:
        print("❌ CONFLICT FOUND: You are loading a local file instead of the library!")
        print(f"This file is the problem: {location}")
        
        # 4. Auto-fix: Rename the bad file
        new_name = location + ".backup_junk"
        try:
            os.rename(location, new_name)
            print(f"✅ FIXED: I renamed the bad file to '{os.path.basename(new_name)}'.")
            print("Please restart your Streamlit app now.")
        except Exception as e:
            print(f"Could not rename automatically. Please delete this file manually: {location}")

except ImportError:
    print("❌ ERROR: The library 'youtube-transcript-api' is not installed.")
    print("Run: pip install youtube-transcript-api")

except AttributeError:
    # If the import itself crashes, we try to find the file via file system
    print("❌ ATTRIBUTE ERROR: The import crashed.")
    print("Checking current directory for 'youtube_transcript_api.py'...")
    if os.path.exists("youtube_transcript_api.py"):
        print("FOUND IT: 'youtube_transcript_api.py' exists in this folder.")
        os.rename("youtube_transcript_api.py", "youtube_transcript_api.py.bak")
        print("✅ FIXED: Renamed it to .bak")
    else:
        print("Could not automatically find the file. Check your 'src' folder.")

print("--- DIAGNOSTIC END ---")