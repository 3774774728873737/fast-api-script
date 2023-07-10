from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
import cv2
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import subprocess
import time
import random
import string
import os
import base64

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_unique_filename():
    timestamp = str(int(time.time()))
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    unique_filename = timestamp + '_' + random_string
    return unique_filename


@app.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...)):
    unique_filename = generate_unique_filename() + ".mp3"
    with open(unique_filename, "wb") as f:
        f.write(await file.read())
    time.sleep(4)
    return {"message": "Audio uploaded successfully", "filename": unique_filename}


@app.post("/upload-videos")
async def upload_videos(files: List[UploadFile] = File(...)):
    filenames = []
    for file in files:
        unique_filename = generate_unique_filename() + ".mp4"
        with open(unique_filename, "wb") as f:
            f.write(await file.read())
        filenames.append(unique_filename)
    return {"message": "Videos uploaded successfully", "filenames": filenames}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...), videoNumber: int = Form(...)):
    unique_filename = generate_unique_filename() + ".mp4"
    with open(unique_filename, "wb") as f:
        f.write(await file.read())

    # Generate thumbnail image for the uploaded video
    video_capture = cv2.VideoCapture(unique_filename)
    success, frame = video_capture.read()
    if success:
        # Save the thumbnail as a temporary file
        thumbnail_path = unique_filename.replace(".mp4", ".jpg")
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
    audio_merge = ";"
    input_files = ""
    audios = ""
    audio_mapping = ""
    for i, file in enumerate(files, start=1):
        file_name = generate_unique_filename() + ".mp4"
        with open(file_name, "wb") as f:
            f.write(await file.read())

        input_files += f"-i {file_name} "
        command = ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_type', '-of', 'default=noprint_wrappers=1:nokey=1', file_name]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip() == 'audio':
            audio_merge += f"[{i - 1}:a]"

    if audio is not None:
        audio_name = generate_unique_filename() + ".mp3"
        with open(audio_name, "wb") as f:
            f.write(await audio.read())
        audios = f"-i {audio_name}"
        audio_merge += "[3:a]"
    audio_merge += f"amerge=inputs={len(files)}[a]"

    if len(files) > 0:
        audio_mapping = "-map \"[a]\""

    output_name = generate_unique_filename() + ".mp4"
    command = f"""ffmpeg -y {input_files} {audios} -vsync 2 -filter_complex "[0:v]scale=426:720[v0];[1:v]scale=426:720[v1];[2:v]scale=426:720[v2];[v0][v1][v2]hstack=3,scale=1280:720[v];{audio_merge} " -map "[v]" {audio_mapping} -c:v libx264 -crf 23 -preset veryfast -c:a libmp3lame -b:a 128k {output_name}"""
    subprocess.run(command, shell=True)

    return FileResponse(output_name, media_type="video/mp4")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
