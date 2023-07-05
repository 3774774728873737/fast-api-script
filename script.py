from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
import cv2
from fastapi.middleware.cors import CORSMiddleware
from moviepy.editor import VideoFileClip, clips_array, concatenate_videoclips
from moviepy.editor import *
from moviepy.audio.AudioClip import AudioArrayClip, concatenate_audioclips
import os
import base64
import uvicorn
from typing import List


global audioname
audioname = None


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)



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


@app.post("/combine")
async def combine_videos(files: List[UploadFile] = File(...), audio: UploadFile = File(None)):
    video_clips = []
    audio_clips = []
    
    for i, file in enumerate(files, start=1):
        with open(f"video{i}2.mp4", "wb") as f:
            f.write(await file.read())
        video_clip = VideoFileClip(f"video{i}2.mp4")
        video_clips.append(video_clip)
        
    if audio is not None:
        with open("audio232.mp3", "wb") as f:
            f.write(await audio.read())
        audio_clip = AudioFileClip("audio232.mp3")
        audio_clips.append(audio_clip)

    final_clip = concatenate_videoclips(video_clips)
    final_audio = concatenate_audioclips(audio_clips) if audio_clips else None
    
    if final_audio is not None:
        final_clip = final_clip.set_audio(final_audio)
        
    final_clip.write_videofile("test.mp4", codec="libx264", audio_codec="aac", temp_audiofile="temp-audio.m4a", remove_temp=True)
    
    for clip in video_clips:
        clip.reader.close()
        clip.audio.reader.close_proc()
    if final_audio is not None:
        final_audio.reader.close_proc()

    return FileResponse("test.mp4", media_type="video/mp4")

