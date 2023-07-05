from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
import cv2
from fastapi.middleware.cors import CORSMiddleware
from moviepy.editor import VideoFileClip, clips_array
from moviepy.editor import *
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

    # Provide the file for download
    response = FileResponse(file.filename, media_type="audio/mpeg")
    response.headers["Content-Disposition"] = f'attachment; filename="{file.filename}"'
    return response


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
async def combine_videos(files: List[UploadFile] = File(...)):

    for i, file in enumerate(files, start=1):
        with open(f"video{i}2.mp4", "wb") as f:
            f.write(await file.read())

    global audioname

    videos = ["video12.mp4", "video22.mp4", "video32.mp4"]
    length = 6

    clip1 = VideoFileClip("video12.mp4").subclip(0, 0 + length)
    # get audio of clip
    aud1 = clip1.audio
    clip2 = VideoFileClip("video22.mp4").subclip(0, 0 + length)
    # get audio of clip
    aud2 = clip2.audio
    clip3 = VideoFileClip("video32.mp4").subclip(0, 0 + length)
    # get audio of clip
    aud3 = clip3.audio

    width = 426
    height = 720

    combined = clips_array([[clip1, clip2, clip3]])

    output_width = 1280
    output_height = 720

    combined2 = combined.resize((output_width, output_height))

    if audioname != None:
        print("runs")
        # Trim audio clip to match the duration of the video
        audio = AudioFileClip(audioname).subclip(0, combined2.duration)
        composite_audio = CompositeAudioClip([audio, aud1, aud2, aud3])
        combined2 = combined2.set_audio(composite_audio)
        combined2.write_videofile("test.mp4")
        audio.reader.close_proc()

    else:
        print("not runs")
        combined2.write_videofile("test.mp4")

    # close
    audioname = None

    return FileResponse("test.mp4", media_type="video/mp4")

