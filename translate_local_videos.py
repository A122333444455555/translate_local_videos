import copy
import shutil
import whisper
import ffmpeg
import os
import sys
import platform
from deep_translator import GoogleTranslator
from datetime import timedelta
if platform.system().lower() != "windows":
    import shlex

MIN_PYTHON = (3, 8)
if sys.version_info < MIN_PYTHON:
    sys.exit(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or higher is required."
    f"You are using {sys.version_info.major}.{sys.version_info.minor}.")

# === CONFIG ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FFMPEG_BIN = os.path.join(BASE_DIR, "ffmpeg", "bin")
if platform.system().lower() == "windows":
    ffmpeg_exe = os.path.join(FFMPEG_BIN, "ffmpeg.exe")
else:  # Linux / Mac
    ffmpeg_exe = os.path.join(FFMPEG_BIN, "ffmpeg")  # no .exe

if os.path.isfile(ffmpeg_exe):
    os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ.get("PATH", "")
else:
    print("Warning: ffmpeg not found. Make sure ffmpeg/bin is present.")

# Input directory containing videos to process
input_dir = os.path.join(BASE_DIR, "videos_to_process")  # <-- Specify your directory with video files
output_dir = os.path.join(BASE_DIR, "processed_videos")  # <-- Specify where to save processed videos
os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

whisper_model = "medium"        # Model: tiny, base, small, medium, large
embed_subs = True              # Hardcode subtitles into video (True/False)
target_language = "ro"         # Language code for translation (Romanian)

def format_time(seconds):
    """Convert seconds to SRT timestamp format"""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    millis = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def safe_remove(path):
    """Delete file safely without crashing."""
    if path and os.path.exists(path):
        try:
            os.remove(path)
            print(f"Deleted: {path}")
        except Exception as e:
            print(f"Could not delete {path}: {e}")

def create_srt_file(segments, srt_path, target_language="ro"):
    """Create SRT from Whisper segments and translate"""
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, start=1):
            start = format_time(seg['start'])
            end = format_time(seg['end'])
            text = seg['text'].strip()

            # Translate segment text
            if target_language != "auto":
                try:
                    text = GoogleTranslator(source='auto', target=target_language).translate(text)
                except Exception as e:
                    print(f"Translation error: {e}, keeping original text")

            f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

def process_video(video_file, video_counter):
    audio_file = None
    srt_file = None
    srt_file2 = None
    output_video = None
    try:
        print(f"\nProcessing: {video_file}")

        # === Extract Audio ===
        audio_file = os.path.join(output_dir, f"audio{video_counter}.wav")
        ffmpeg.input(video_file).output(audio_file, ac=1, ar=16000).run(overwrite_output=True)
        print("Audio extracted.")

        # === Generate Whisper transcription (segments) ===
        print("Transcribing audio with Whisper...")
        result = model.transcribe(audio_file)
        segments = result['segments']
        print("Transcription done.")

        # === Create Translated SRT ===
        srt_file = os.path.splitext(video_file)[0] + f"_{target_language}.srt"
        srt_file2 = copy.deepcopy(srt_file)
        create_srt_file(segments, srt_file, target_language=target_language)
        print(f"Translated SRT saved: {srt_file}")
        if platform.system().lower() == "windows":
            srt_file = srt_file.replace('\\', '\\\\').replace(":", "\\:")
        else:
            srt_file = shlex.quote(srt_file)
        
        # === Embed Subtitles ===
        if embed_subs:
            output_video = os.path.splitext(video_file)[0] + f"_{target_language}_with_subs.mp4"
            ffmpeg.input(video_file).output(
                output_video,
                filter_complex=f"subtitles='{srt_file}'",
                vcodec="libx264",
                acodec="aac"
            ).run(overwrite_output=True)
            print(f"Video with subtitles saved: {output_video}")
            shutil.move(output_video, output_dir)

    except Exception as e:
        print(f"Error processing {video_file}: {e}")
    finally:
        # === CLEANUP TEMP FILES ===
        safe_remove(audio_file)
        if embed_subs:
            safe_remove(srt_file2)

def main():
    # Get list of video files in the specified directory
    video_counter = 1
    for filename in os.listdir(input_dir):
        # Check if the file is a video (you can adjust the extensions if needed)
        if filename.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
            video_file = os.path.join(input_dir, filename)
            process_video(video_file, video_counter)
            video_counter += 1

if __name__ == "__main__":
    print(f"Loading Whisper model: {whisper_model}...")
    try:
        model = whisper.load_model(whisper_model)
    except Exception as e:
        print(f"Error loading Whisper model: {e}")
        sys.exit(1)
    try:
        main()
    except Exception as e:
        print(f"Unexpected error occurred in main: {e}")
    finally:
        print("FINALLY ALL DONE!!!")
        sys.exit()
