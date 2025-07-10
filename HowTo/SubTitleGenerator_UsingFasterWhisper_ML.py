"""
https://www.digitalocean.com/community/tutorials/how-to-generate-and-add-subtitles-to-videos-using-python-openai-whisper-and-ffmpeg
"""
import math
import ffmpeg
from faster_whisper import WhisperModel

# variables
input_video = "C:\\TMP\\SubtitlesTranscriberAlt\\video.mp4"
input_video_name = input_video.replace(".mp4", "")

def extract_audio():
    print(f"   * Extracting audio from video as '.mp3' file...", end="")
    extracted_audio = f"{input_video_name}.mp3"
    stream = ffmpeg.input(input_video)
    stream = ffmpeg.output(stream, extracted_audio)
    ffmpeg.run(stream, overwrite_output=True, quiet=True)
    print(f" [OK]")
    return extracted_audio

def transcribe(audio):
    print(f"   * Transcribing (prev. extracted) audio...")
    model = WhisperModel("small", device="cpu", compute_type="int8") # cuda = GPU, cpu=CPU, int8 or float16=comp_type
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
    print(f"   * Formatting transcribed texts into '.srt' subtitle format...",end="")
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
    extracted_audio = extract_audio()
    language, segments = transcribe(audio=extracted_audio)
    generate_subtitle_file(language=language, segments=segments)
    print(f" * [DONE!]")
run()