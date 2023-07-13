from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
import cv2
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import subprocess
import os
import uuid

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your desired origins
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return Response(content=open("index.html", "r").read(), media_type="text/html")

@app.post("/upload-audio")
async def upload_audio(audio: UploadFile = File(None)):
    if audio:
        unique_id = str(uuid.uuid4())
        audio_file_name = f"static/audio_{unique_id}.mp3"
        with open(audio_file_name, "wb") as f:
            f.write(await audio.read())
        return JSONResponse({"message": "Audio uploaded successfully", "unique_id": unique_id})
    else:
        return JSONResponse({"message": "No audio uploaded"})

@app.post("/upload")
async def upload_file(files: List[UploadFile] = File(...), videoNumber: int = Form(...)):
    unique_id = str(uuid.uuid4())
    width = 426
    height = 720
    video_files = []
    for file in files:
        temp_file_name = f"static/temp_{unique_id}_{file.filename}"
        with open(temp_file_name, "wb") as f:
            f.write(await file.read())

        resized_file_name = f"static/resized_{unique_id}_{file.filename}"
        print("File name: ", file.filename)
        subprocess.run([
            "ffmpeg", "-i", temp_file_name, "-vf",
            f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}",
            resized_file_name
        ])
        video_files.append(resized_file_name)

    # concatenate videos into one
    list_file = f"static/list_{unique_id}.txt"
    with open(list_file, "w") as f:
        for video_file in video_files:
            f.write(f"file '{os.path.join(os.getcwd(), video_file)}'\n")

    # concatenate videos into one
    final_clip_name = f"static/video_{unique_id}_{videoNumber}.mp4"
    subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", final_clip_name])
    os.remove(list_file)  # remove the list file
    # Generate thumbnail image for the uploaded video
    video_capture = cv2.VideoCapture(final_clip_name)
    success, frame = video_capture.read()
    if success:
        thumbnail_path = f"static/thumbnail_{unique_id}_{videoNumber}.jpg"
        cv2.imwrite(thumbnail_path, frame)
    else:
        thumbnail_path = None

    return JSONResponse({"message": "Videos uploaded successfully", "imagePath": thumbnail_path, "unique_id": unique_id})

@app.get("/combine/{unique_ids}/{audio_id}")
async def combine_videos(unique_ids: str, audio_id: str = None):

    for file in os.listdir("static"):
        if file.startswith("test_"):
            os.remove(os.path.join("static", file))

    unique_ids = unique_ids.split(",")
    videos = [f"static/video_{unique_id}_{i+1}.mp4" for i, unique_id in enumerate(unique_ids)]
    
    width = 426
    height = 720
    unique_id = str(uuid.uuid4())
    video_filters = []
    # ffmpeg command to generate the combined video
    ffmpeg_command = ["ffmpeg"]
    for i, video in enumerate(videos):
        ffmpeg_command.extend(["-i", video])
        video_filters.append(f"[{i}:v]scale=640:-1[v{i}]")
        video_filters.append(f"[{i}:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[a{i}]")

    if audio_id:  # if audio_id is provided, add it to the ffmpeg command
        ffmpeg_command.extend(["-i", f"static/audio_{audio_id}.mp3"])
        video_filters.append(f"[{len(videos)}:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[a{len(videos)}]")
        video_filters.append(f'{"[" + "][".join([f"a{i}" for i in range(len(videos) + 1)])}]amix=inputs={len(videos) + 1}[a]')
    else:
        video_filters.append(f'{"[" + "][".join([f"a{i}" for i in range(len(videos))])}]amix=inputs={len(videos)}[a]')

    # # Combine the videos into a grid and mix the audio
    # output_width = 1280
    # output_height = 720

    video_filters.append(f'{"[" + "][".join([f"v{i}" for i in range(len(videos))])}]hstack=inputs={len(videos)}[v]')

    ffmpeg_command.extend(["-filter_complex", '; '.join(video_filters), "-map", "[v]", "-map", "[a]", "-b:v", "4096k", "-preset", "fast", "-t", "30", f"static/test_{unique_id}.mp4"])
    subprocess.run(ffmpeg_command)

    # remove all the temporary files
    for video in videos:
        os.remove(video)
    
    for file in os.listdir("static"):
        if file.startswith("video_") or file.startswith("resized_") or file.startswith("temp_") or file.startswith("thumbnail_") or file.startswith("audio_"):
            os.remove(os.path.join("static", file))
    
    return FileResponse(f"static/test_{unique_id}.mp4", media_type="video/mp4")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
