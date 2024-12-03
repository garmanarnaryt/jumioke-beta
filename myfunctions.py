import requests
import cv2
import datetime
import json
import sys
import tempfile
from pydub import AudioSegment
import os
import ffmpeg
from faster_whisper import WhisperModel
import json
from tqdm import tqdm
import demucs.separate
import shlex
#from moviepy.editor import TextClip, CompositeVideoClip, ColorClip
import numpy as np
import time
#import youtube_dl
from yt_dlp import YoutubeDL, DownloadError
import yt_dlp
import tempfile
from myfunctions import *
from datetime import datetime
import os
import shutil

def ytDownloader(name):
    #youtube downloader
    urls =  input("url:")
    
    if urls == "last":
        audiofilename = ""
    else:
        
        vid = YouTube(urls)

        #video_download = vid.streams.get_highest_resolution()
        audio_download = vid.streams.get_audio_only()

        entry = YouTube(urls).title

        print(f"\nVideo found: {entry}\n")
        print("Downloading Audio...")
        audio_download.download(filename= "static/assets/music/" + name + ".mp3")
        print("Program Completed")

    time.sleep(1)
    audiofilename = name + ".mp3"
    return audiofilename

def TransAssembly(name):
    base_url = "https://api.assemblyai.com/v2"

    headers = {
        "authorization": "4350de607a1644ceaa14b8a542bb9789" 
    }

    with open("separated/htdemucs/" + name + "/vocals.wav", "rb") as f:
        response = requests.post(base_url + "/upload",
                                headers=headers,
                                data=f)

        upload_url = response.json()["upload_url"]

    data = {
        "audio_url": upload_url
    }

    url = base_url + "/transcript"
    response = requests.post(url, json=data, headers=headers)

    transcript_id = response.json()['id']
    polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"

    while True:
        transcription_result = requests.get(polling_endpoint, headers=headers).json()

        if transcription_result['status'] == 'completed':
            break

        elif transcription_result['status'] == 'error':
            raise RuntimeError(f"Transcription failed: {transcription_result['error']}")

        else:
            time.sleep(3)


    time.sleep(10)
    print(transcript_id)
    subtitle_text = get_subtitle_file(transcript_id, "srt")
    print(subtitle_text)

    with open('segment.lrc','w') as f:
        for segment in subtitle_text:
            date = datetime.fromtimestamp(segment.start)
            date_time_str = date.strftime('%M:%S')
            millis_str = str(int(date.strftime('%f')[:2]))
            findate_time = date_time_str + "." + millis_str
            #print(findate_time)
            #print(date_time_str)
            #segment_info.append({'segment':segment.text,'start':findate_time})
            f.write("[" + findate_time + "]" + segment.text + "\n")

    f.close()

def get_subtitle_file(transcript_id, file_format):
    headers = {
        "authorization": "4350de607a1644ceaa14b8a542bb9789" 
    }
    if file_format not in ["srt", "vtt"]:
        raise ValueError("Invalid file format. Valid formats are 'srt' and 'vtt'.")

    url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}/{file_format}"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        raise RuntimeError(f"Failed to retrieve {file_format.upper()} file: {response.status_code} {response.reason}")


def TransWhisper(name,path):

    model_size = "medium"

    model = WhisperModelmodel = WhisperModel(model_size,compute_type="int8")

    segments, info = model.transcribe(path,word_timestamps=True) #, vad_filter=True,vad_parameters=dict(min_silence_duration_ms=500))

    segments = list(segments)
    ''' 
    #Word level logic
    for segment in segments:
        for word in segment.words:
            print("[%.2fs -> %.2fs] %s" % (word.start, word.end, word.word))
    
    wordlevel_info  = []



    for segment in segments:
        for word in segment.words:
            wordlevel_info.append({'word':word.word,'start':word.start,'end':word.end})
    '''
    segment_info = []
    with open('segment.lrc','w') as f:
        for segment in segments:
            date = datetime.fromtimestamp(segment.start)
            date_time_str = date.strftime('%M:%S')
            millis_str = str(int(date.strftime('%f')[:2]))
            findate_time = date_time_str + "." + millis_str
            #print(findate_time)
            #print(date_time_str)
            #segment_info.append({'segment':segment.text,'start':findate_time})
            f.write("[" + findate_time + "]" + segment.text + "\n")

    f.close()

    
    time.sleep(1)

def split_text_into_lines(data):

    MaxChars = 200
    #maxduration in seconds
    MaxDuration = 20
    #Split if nothing is spoken (gap) for these many seconds
    MaxGap = 1.5

    subtitles = []
    line = []
    line_duration = 0
    line_chars = 0


    for idx,word_data in enumerate(data):
        word = word_data["word"]
        start = word_data["start"]
        end = word_data["end"]

        line.append(word_data)
        line_duration += end - start

        temp = " ".join(item["word"] for item in line)


        # Check if adding a new word exceeds the maximum character count or duration
        new_line_chars = len(temp)

        duration_exceeded = line_duration > MaxDuration
        chars_exceeded = new_line_chars > MaxChars
        if idx>0:
          gap = word_data['start'] - data[idx-1]['end']
          # print (word,start,end,gap)
          maxgap_exceeded = gap > MaxGap
        else:
          maxgap_exceeded = False


        if duration_exceeded or chars_exceeded or maxgap_exceeded:
            if line:
                subtitle_line = {
                    "word": " ".join(item["word"] for item in line),
                    "start": line[0]["start"],
                    "end": line[-1]["end"],
                    "textcontents": line
                }
                subtitles.append(subtitle_line)
                line = []
                line_duration = 0
                line_chars = 0


    if line:
        subtitle_line = {
            "word": " ".join(item["word"] for item in line),
            "start": line[0]["start"],
            "end": line[-1]["end"],
            "textcontents": line
        }
        subtitles.append(subtitle_line)

    return subtitles

def SeparateStems(audiofilename):
    demucs.separate.main(shlex.split('--two-stems vocals ' + "static/assets/music/" + audiofilename + ' --mp3-preset 7 --int24'))
    print("sleeping 10s to preserve file integrity...")
    time.sleep(10)
    

def moveFiles(source, destination):
    shutil.move(source, destination)
    print("File: " + source + " is moved to " + destination)
    textReturn = "File: " + source + " is moved to " + destination
    return textReturn

def ytprocess(URLS):

    ######DECLARATIONS#####
    demucsSepFolder = "separated/htdemucs/"


    
    ######Input link here#####
    #URLS = input("URL PLX:")


    ######YOUTUBE DOWNLOADER to MP3########
    #URLS = ['https://www.youtube.com/watch?v=iFx-5PGLgb4']

    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'outtmpl': 'Downloaded/%(id)s',
        "cookiefile": "cookie.txt"
        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3'
        }]
    }


    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(URLS)
        info_dict = ydl.extract_info(URLS, download=False)
        video_url = info_dict.get("url", None)
        video_id = info_dict.get("id", None)
        video_title = info_dict.get('title', None)
        print("Title: " + video_title) # <= Here, you got the video title
    ######YOUTUBE DOWNLOADER to MP3########


    ######DEMUCS SEPARATE VOCALS to NON VOCALS#######
    audiofilename = "Downloaded/" + video_id + '.mp3'



    demucs.separate.main(shlex.split('--two-stems vocals ' + audiofilename + ' --mp3-preset 7 --int24'))


    time.sleep(1)

    name = video_id

    TranscribeMp3 = demucsSepFolder + name + "/vocals.wav"

    TransWhisper(name,TranscribeMp3)

    # Transcription Assembly AI
    #transcript = TransAssembly("Downloaded")


    #subtitle_text = get_subtitle_file(transcript, "srt")
    # subtitle_text = get_subtitle_file(transcript_id, "srt")
    #print(subtitle_text)

    print("Transcription Done")

    noVocalSource = demucsSepFolder + name + "/no_vocals.wav"
    noVocalsDestination = "static/assets/music/" + video_id + ".mp3"
    moveFiles(noVocalSource, noVocalsDestination)

    segmentLrcSource = "segment.lrc"
    segmentLrcDestination = "static/lyrics/" + video_id  + ".lrc"
    moveFiles(segmentLrcSource, segmentLrcDestination)

    #Write to file the songs
    myfile = open("static/songs.txt", "a")
    myfile.write("\n" + video_title + "#" + video_id)
    myfile.close()

    #Delete files from downloaded folder

    os.remove(audiofilename)

    #Delete files from demucs folder
    try:
        mydir = "separated/htdemucs/" + video_id
        shutil.rmtree(mydir)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))

