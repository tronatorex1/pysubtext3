"""
install pip install imageio-ffmpeg
https://www.digitalocean.com/community/tutorials/how-to-generate-and-add-subtitles-to-videos-using-python-openai-whisper-and-ffmpeg
"""
import math
import subprocess
import sys
import importlib
try:
    import imageio_ffmpeg
except ModuleNotFoundError:
    print("imageio-ffmpeg not found; installing via pip...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "imageio-ffmpeg"], stdout=subprocess.DEVNULL)
    imageio_ffmpeg = importlib.import_module("imageio_ffmpeg")
from faster_whisper import WhisperModel
import pathlib
import re

# variables
input_video = rf"C:\TMP\x.mp4"
input_video = rf"C:\ALEX\Torrents\Three Kings (1999)\Three.Kings.1999.720p.BrRip.x264.YIFY.mkv"
input_video_name = str(re.findall(r"^.*\d\d\d\d", input_video)[0])
#input_video_name = input_video.replace(".mp4", "")

def extract_audio():
    print(f"   * 1 Extracting audio from video as '.wav' file...", end="")
    extracted_audio = f"{input_video_name}.wav"
    try:
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as e:
        raise RuntimeError("Failed to obtain ffmpeg executable from imageio-ffmpeg. Check installation or try running 'pip install --upgrade imageio-ffmpeg'.") from e
    cmd = [ffmpeg_exe, "-i", input_video, "-vn", "-ac", "1", "-ar", "16000", extracted_audio, "-y"]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        raise RuntimeError("ffmpeg failed to extract audio. Ensure the input file is valid and ffmpeg supports the format.")
    if not pathlib.Path(extracted_audio).exists():
        raise RuntimeError("Failed to create extracted audio file.")
    print(f" [OK]")
    return extracted_audio

def transcribe(audio):
    print(f"   * 2 Transcribing (prev. extracted) audio = {audio}")
    model = WhisperModel(model_size_or_path="small.en", device="cpu", compute_type="int8") # cuda = GPU, cpu=CPU, int8 or float16=comp_type
    segments, info = model.transcribe(audio)
    print(f"     * Detected language: [ {info.language} ], with probability: [ {int(info.language_probability*100)}% ]")
    language = info.language
    segments = list(segments)
    #print(f"Transcription contents: [ {segments} ]")
    #for segment in segments:
    #    print(f"[{str(segment.start).zfill(1)} -> {str(segment.end).zfill(1)}] : '{segment.text.strip()}'")
    return language, segments

def format_time(seconds): # esto formatea los timestamps para que sean compatibles con .SRT
    hours = math.floor(seconds / 3600)
    seconds %= 3600
    minutes = math.floor(seconds / 60)
    seconds %= 60
    milliseconds = round((seconds - math.floor(seconds)) * 1000)
    seconds = math.floor(seconds)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:01d}"
    return formatted_time

def generate_subtitle_file(language,segments):
    print(f"   * 3 Formatting transcribed texts into '.srt' subtitle format...",end="")
    subtitle_file = f"{input_video_name}.{language}.srt"
    text = ""
    for index,segment in enumerate(segments):
        segment_start = format_time(segment.start) # aquí se invoca el formateador de timestamp
        segment_end = format_time(segment.end) # aquí se invoca el formateador de timestamp
        text += f"{str(index + 1)} \n"
        text += f"{segment_start} --> {segment_end} \n"
        text += f"{segment.text} \n"
        text += "\n"
    f = open(subtitle_file,"w")
    f.write(text)
    f.close()
    print(f" [OK]")
    return subtitle_file

def run():
    print(f" * Faster Whisper Lib: extracts texts from audio files (from movie files)...")
    print(f" File = {input_video}")
    extracted_audio = extract_audio()
    language, segments = transcribe(audio=extracted_audio)
    generate_subtitle_file(language=language, segments=segments)
    print(f" * [DONE!]")


if __name__ == '__main__':
    run()
