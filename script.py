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
    for i, file in enumerate(files, start=1):
        with open(f"video{i}2.mp4", "wb") as f:
            f.write(await file.read())

    if audio is not None:
        # Save the uploaded audio file
        with open("audio232.mp3", "wb") as f:
            f.write(await audio.read())

    else:
        print("no audio")

    global audioname

    videos = ["video12.mp4", "video22.mp4", "video32.mp4"]
    length = 6

    chunk_duration = 2  # Duration of each chunk in seconds

    processed_chunks = []
    output_width = 1280
    output_height = 720

    # Process each chunk separately
    for i, video in enumerate(videos, start=1):
        clip = VideoFileClip(video).subclip(0, 0 + length)

        # Get the audio of the clip
        audio_clip = clip.audio

        # Split the clip into chunks
        num_chunks = int(clip.duration / chunk_duration)
        for j in range(num_chunks):
            start_time = j * chunk_duration
            end_time = (j + 1) * chunk_duration

            # Process the chunk
            processed_chunk = clip.subclip(start_time, end_time).resize((output_width, output_height))

            if audio is not None:
                # Trim audio clip to match the duration of the chunk
                audio_chunk = audio_clip.subclip(start_time, end_time)
                composite_audio = CompositeAudioClip([audio_chunk, audio])
                processed_chunk = processed_chunk.set_audio(composite_audio)

            # Store the processed chunk
            processed_chunks.append(processed_chunk)

    # Concatenate the processed chunks to create the final video
    final_clip = concatenate_videoclips(processed_chunks)

    # Write the final video file
    final_clip.write_videofile("test.mp4")

    # Close the clips
    final_clip.close()
    for chunk in processed_chunks:
        chunk.close()

    return FileResponse("test.mp4", media_type="video/mp4")

