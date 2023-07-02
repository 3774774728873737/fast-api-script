from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
import subprocess
from fastapi.middleware.cors import CORSMiddleware
from moviepy.editor import VideoFileClip, clips_array
from moviepy.editor import *
import os
import cv2
import uvicorn


global audioname
audioname = None


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your desired origins
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/delete")
async def delete():
    if os.path.exists("test.mp4"):
        os.remove("test.mp4")



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




@app.get("/combine")
async def combine_videos():
    
    global audioname
   
    videos = ["video1.mp4", "video2.mp4", "video3.mp4"]
    length = 6

    clip1 = VideoFileClip("video1.mp4").subclip(0, 0 + length)
    # get audio of clip
    aud1 = clip1.audio
    clip2 = VideoFileClip("video2.mp4").subclip(0, 0 + length)
    # get audio of clip
    aud2 = clip2.audio
    clip3 = VideoFileClip("video3.mp4").subclip(0, 0 + length)
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

    # close all 
    clip1.reader.close()
    clip2.reader.close()
    clip3.reader.close()

    # close audio
    aud1.reader.close_proc()
    aud2.reader.close_proc()
    aud3.reader.close_proc()



    # remove videos
    os.remove("video1.mp4")
    os.remove("video2.mp4")
    os.remove("video3.mp4")

    # remove thumbnail
    os.remove("thumbnail1.jpg")
    os.remove("thumbnail2.jpg")
    os.remove("thumbnail3.jpg")
        
    return FileResponse("test.mp4", media_type="video/mp4")
    return send_file('test.mp4', as_attachment=True)




#import uvicorn
#uvicorn.run(app, host="localhost", port=8000)
