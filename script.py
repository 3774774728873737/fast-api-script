from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
import cv2
from moviepy.editor import VideoFileClip, clips_array
from moviepy.editor import concatenate_videoclips
from typing import List
from moviepy.editor import *
import os
from moviepy.video.fx.all import crop

from fastapi.middleware.cors import CORSMiddleware
from moviepy.editor import VideoFileClip, clips_array
from moviepy.editor import *
import os
import base64
import uvicorn
from typing import List
import subprocess
import time
import random
import string
global audioname
from collections import Counter


audioname = None


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



def resize_videos(clips, width, height):


    outnames = []

    for clip in clips:
        file1 = generate_unique_filename()


        clip = VideoFileClip(clip)

        # Determine the aspect ratio of the input clip
        aspect_ratio = clip.w / clip.h
        
        # If the aspect ratio of the input clip is greater than the desired aspect ratio
        # it means that the clip is wider and we need to crop it horizontally
        if aspect_ratio > width / height:
            new_width = int(height * aspect_ratio)
            new_height = height
        else:
            new_width = width
            new_height = int(width / aspect_ratio)

        # Resize the clip to the new dimensions
        clip = clip.resize((new_width, new_height))

        # Crop the clip to the desired dimensions
        clip = crop(clip, width=width, height=height, x_center=clip.w / 2, y_center=clip.h / 2)

        # save 
        clip.write_videofile(f"{file1}resized.mp4")

        outnames.append(f"{file1}resized.mp4")

    out = concatenate_videos(outnames, f"{file1}concat.mp4")

    return out


def resize_single(clip, width, height):

    clip = VideoFileClip(clip)

    file1 = generate_unique_filename()

    # Determine the aspect ratio of the input clip
    aspect_ratio = clip.w / clip.h
    
    # If the aspect ratio of the input clip is greater than the desired aspect ratio
    # it means that the clip is wider and we need to crop it horizontally
    if aspect_ratio > width / height:
        new_width = int(height * aspect_ratio)
        new_height = height
    else:
        new_width = width
        new_height = int(width / aspect_ratio)

    # Resize the clip to the new dimensions
    clip = clip.resize((new_width, new_height))

    # Crop the clip to the desired dimensions
    clip = crop(clip, width=width, height=height, x_center=clip.w / 2, y_center=clip.h / 2)

    # save 
    clip.write_videofile(f"{file1}resized.mp4")

    return f"{file1}resized.mp4"


def concatenate_videos(input_files, output_file):
    txt = generate_unique_filename()

    with open(f'{txt}.txt', 'w') as f:
        for file in input_files:
            f.write(f"file '{file}'\n")
    subprocess.run(['ffmpeg', '-f', 'concat', '-safe', '0', '-i', f'{txt}.txt', '-c', 'copy', output_file])

    return output_file



@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    # Save the uploaded audio file
    i = 1
    while True:
        if os.path.exists(f"audio{i}.mp3"):
            i += 1
        else:
            break

    with open(f"audio{i}.mp3", "wb") as f:
        f.write(await file.read())

    global audioname
    audioname = f"audio{i}.mp3"
    time.sleep(4)

    return {"message": "Videos uploaded successfully"}


@app.post("/upload-videos")
async def upload_videos(files: List[UploadFile] = File(...)):
    print(files)
    i = 1
    for file in files:
        with open(f"video{i}.mp4", "wb") as f:
            f.write(await file.read())
        i+=1

    return {"message": "Videos uploaded successfully"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), videoNumber: int = Form(...)):
    with open(f"video{videoNumber}.mp4", "wb") as f:
        f.write(await file.read())

    # Generate thumbnail image for the uploaded video
    video_capture = cv2.VideoCapture(f"video{videoNumber}.mp4")
    success, frame = video_capture.read()
    if success:
        # Save the thumbnail as a temporary file
        thumbnail_path = f"thumbnail{videoNumber}23.jpg"
        cv2.imwrite(thumbnail_path, frame)

        # Read the thumbnail image and convert it to base64
        with open(thumbnail_path, "rb") as thumbnail_file:
            thumbnail_data = thumbnail_file.read()
            thumbnail_base64 = base64.b64encode(thumbnail_data).decode("utf-8")

    else:
        thumbnail_base64 = None

        
    return JSONResponse({"message": "Video uploaded successfully", "imagePath": thumbnail_base64})



def generate_unique_filename():
    timestamp = str(int(time.time()))
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    unique_filename = timestamp + '_' + random_string
    return unique_filename



@app.post("/combine")
async def combine_videos(files: List[UploadFile] = File(...), audio: UploadFile = File(None), videoNumber: str = Form(...)):

    file1 = generate_unique_filename()
    audionames = generate_unique_filename()
    outputname = generate_unique_filename()

    files_na = []
    i = 1
    for i, file in enumerate(files, start=1):
        with open(f"{file1}{i}.mp4", "wb") as f:
            f.write(await file.read())
            files_na.append(f"{file1}{i}.mp4")
        i+=1


    no = videoNumber.split(",")
    # remove empty string from list
    no = list(filter(None, no))
    count = Counter(no)


    # iterate the count
    total_vid =[]
    index = 0
    for key, value in count.items():
        if int(value) > 1:
            joined_names = []
            for x in range(int(value)):
                joined_names.append(files_na[index])
                index = index + 1
            out = resize_videos(joined_names, width=426, height=720)
            total_vid.append(out)
        else:
            out = resize_single(files_na[index], width=426, height=720)
            total_vid.append(out)
            index = index + 1

    input()

    count = 0

    if audio is not None:
        # Save the uploaded audio file
        with open(f"{audionames}.mp3", "wb") as f:
            f.write(await audio.read())
            audios = f"-i {audionames}.mp3"
            count = count + 1

    else:
        audios = ""
        print("no audio")


    if audios != "":
        video1 = total_vid[0]
        video2 = total_vid[1]
        video3 = total_vid[2]

        output_file = f"{outputname}.mp4"
        output_width = 1280
        output_height = 720

        # Determine the duration of each video
        duration1 = float(subprocess.check_output(['ffprobe', '-i', video1, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")]))
        duration2 = float(subprocess.check_output(['ffprobe', '-i', video2, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")]))
        duration3 = float(subprocess.check_output(['ffprobe', '-i', video3, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")]))
        longest_duration = max(duration1, duration2, duration3)

        # Determine the audio start time and duration for each video
        audio_start_time1 = float(subprocess.check_output(['ffprobe', '-i', video1, '-show_entries', 'stream=start_time', '-select_streams', 'a:0', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")]))
        audio_duration1 = longest_duration - audio_start_time1 if audio_start_time1 > 0 else longest_duration

        audio_start_time2 = float(subprocess.check_output(['ffprobe', '-i', video2, '-show_entries', 'stream=start_time', '-select_streams', 'a:0', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")]))
        audio_duration2 = longest_duration - audio_start_time2 if audio_start_time2 > 0 else longest_duration

        audio_start_time3 = float(subprocess.check_output(['ffprobe', '-i', video3, '-show_entries', 'stream=start_time', '-select_streams', 'a:0', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")]))
        audio_duration3 = longest_duration - audio_start_time3 if audio_start_time3 > 0 else longest_duration

        # Calculate the duration of the external audio file
        external_audio_duration = float(subprocess.check_output(['ffprobe', '-i', f"{audionames}.mp3", '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")]))

        # Determine the final audio duration
        final_audio_duration = min(longest_duration, external_audio_duration)

        # Construct the filtergraph for combining videos side by side with audio
        filtergraph = f"[0:v]scale=426:720[v0_scaled];[1:v]scale=426:720[v1_scaled];[2:v]scale=426:720[v2_scaled];"
        filtergraph += "[v0_scaled][v1_scaled][v2_scaled]hstack=inputs=3[v];"

        # Add adelay filter for each video's audio
        filtergraph += f"[0:a]adelay={int((audio_start_time1)*1000)}|{int((audio_duration1)*1000)}[a1];" if audio_start_time1 > 0 else "[0:a]anull[a1];"
        filtergraph += f"[1:a]adelay={int((audio_start_time2)*1000)}|{int((audio_duration2)*1000)}[a2];" if audio_start_time2 > 0 else "[1:a]anull[a2];"
        filtergraph += f"[2:a]adelay={int((audio_start_time3)*1000)}|{int((audio_duration3)*1000)}[a3];" if audio_start_time3 > 0 else "[2:a]anull[a3];"

        # Mix all audio streams, including the external audio file
        filtergraph += f"[a1][a2][a3][3:a]amix=inputs=4[a]"

        # Construct the ffmpeg command
        ffmpeg_cmd = ['ffmpeg',
                    '-i', video1,
                    '-i', video2,
                    '-i', video3,
                    '-i', f"{audionames}.mp3",
                    '-filter_complex', filtergraph,
                    '-map', '[v]',
                    '-map', '[a]',
                    '-t', str(final_audio_duration),
                    '-c:v', 'libx264',
                    '-c:a', 'aac',  # Output audio codec
                    '-crf', '18',
                    '-preset', 'fast',
                    '-y',
                    output_file]

        # Run the ffmpeg command
        subprocess.run(ffmpeg_cmd)


    else:
        video1 = total_vid[0]
        video2 = total_vid[1]
        video3 = total_vid[2]

        output_file = f"{outputname}.mp4"
        output_width = 1280
        output_height = 720

        # Determine the duration of each video
        duration1 = float(subprocess.check_output(['ffprobe', '-i', video1, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")]))
        duration2 = float(subprocess.check_output(['ffprobe', '-i', video2, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")]))
        duration3 = float(subprocess.check_output(['ffprobe', '-i', video3, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")]))
        longest_duration = max(duration1, duration2, duration3)

        # Determine the audio start time for each video
        audio_start_time1 = float(subprocess.check_output(['ffprobe', '-i', video1, '-show_entries', 'stream=start_time', '-select_streams', 'a:0', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")]))
        audio_start_time2 = float(subprocess.check_output(['ffprobe', '-i', video2, '-show_entries', 'stream=start_time', '-select_streams', 'a:0', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")]))
        audio_start_time3 = float(subprocess.check_output(['ffprobe', '-i', video3, '-show_entries', 'stream=start_time', '-select_streams', 'a:0', '-v', 'quiet', '-of', 'csv=%s' % ("p=0")]))
        max_audio_start_time = max(audio_start_time1, audio_start_time2, audio_start_time3)

        # Construct the filtergraph for combining videos side by side with audio
        filtergraph = f"[0:v]scale=426:720[v0_scaled];[1:v]scale=426:720[v1_scaled];[2:v]scale=426:720[v2_scaled];"
        filtergraph += "[v0_scaled][v1_scaled][v2_scaled]hstack=inputs=3[v];"

        # Check and handle delayed audio for each video
        filtergraph += f"[0:a]adelay={int((audio_start_time1-max_audio_start_time)*1000)}[a1];" if audio_start_time1 > 0 else "[0:a]anull[a1];"
        filtergraph += f"[1:a]adelay={int((audio_start_time2-max_audio_start_time)*1000)}[a2];" if audio_start_time2 > 0 else "[1:a]anull[a2];"
        filtergraph += f"[2:a]adelay={int((audio_start_time3-max_audio_start_time)*1000)}[a3];" if audio_start_time3 > 0 else "[2:a]anull[a3];"

        filtergraph += "[a1][a2][a3]amix=inputs=3[a]"  # Mix all audio streams together

        # Construct the ffmpeg command
        ffmpeg_cmd = ['ffmpeg',
                    '-i', video1,
                    '-i', video2,
                    '-i', video3,
                    '-filter_complex', filtergraph,
                    '-map', '[v]',
                    '-map', '[a]',
                    '-t', str(longest_duration),
                    '-c:v', 'libx264',
                    '-c:a', 'aac',  # Output audio codec
                    '-crf', '18',
                    '-preset', 'fast',
                    '-y',
                    output_file]

        # Run the ffmpeg command
        subprocess.run(ffmpeg_cmd)

    return FileResponse(f"{outputname}.mp4", media_type="video/mp4")

