Quick Reference – translate_local_videos.py

1. Install Python 3.8+ and dependencies from requirements.txt
2. Ensure ffmpeg is installed and its path is set in the script
3. Place videos in the "videos_to_process" folder
4. Run the script:
   - Windows: python translate_local_videos.py OR py translate_local_videos.py
   - Linux / Mac: python3 translate_local_videos.py
5. Output videos appear in the "processed_videos" folder
6. Windows path handling for subtitles:
   - Replace all ":" with "\:" (required in CMD and IDEs)
   - Replace all "\" with "\\" ONLY in CMD; not needed in IDEs like PyCharm
7. Troubleshooting:
   - Ensure video filenames have no unusual symbols
   - Verify ffmpeg path in the script; hardcode if needed

NOTE: An internet connection is needed for the translation step, 
as Google Translator fetches translations online. 
If embed_subs is set to True, the .srt files will be deleted 
at the end after being hardcoded into the video.
For subtitles, the language code must match the target_language specified in the script.
You can download and install ffmpeg for Windows (choose the "essentials" static build) from:
https://www.gyan.dev/ffmpeg/builds/
