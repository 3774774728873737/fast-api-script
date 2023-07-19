from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
import cv2
import subprocess
from fastapi.middleware.cors import CORSMiddleware
from moviepy.editor import VideoFileClip, clips_array
from moviepy.editor import concatenate_videoclips
from typing import List
from moviepy.editor import *
import os
from moviepy.video.fx.all import crop



global audioname
audioname = None



def resize_video(clip, width, height):
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

    return clip


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your desired origins
    allow_methods=["*"],
    allow_headers=["*"],
)






@app.post("/upload")
async def upload_file(files: List[UploadFile] = File(...), videoNumber: int = Form(...)):
    video_clips = []

    for file in files:
        temp_file_name = f"temp{file.filename}"
        with open(temp_file_name, "wb") as f:
            f.write(await file.read())
        width = 426
        height = 720
        video_clips.append(resize_video(VideoFileClip(temp_file_name), width, height))
        # video_clips.append(VideoFileClip(temp_file_name))
    
    # concatenate videos into one
    final_clip = concatenate_videoclips(video_clips, method='compose')
    final_clip_name = f"video{videoNumber}.mp4"
    final_clip.write_videofile(final_clip_name)

    # Generate thumbnail image for the uploaded video
    video_capture = cv2.VideoCapture(final_clip_name)
    success, frame = video_capture.read()
    if success:
        thumbnail_path = f"thumbnail{videoNumber}.jpg"
        cv2.imwrite(thumbnail_path, frame)
    else:
        thumbnail_path = None

    return JSONResponse({"message": "Videos uploaded successfully", "imagePath": thumbnail_path})



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





    
@app.get("/combine")
async def combine_videos():


    global audioname

    
    clip1 = VideoFileClip("video1.mp4")
    clip2 = VideoFileClip("video2.mp4")
    clip3 = VideoFileClip("video3.mp4")

    width = 426
    height = 720

    clip1 = resize_video(VideoFileClip("video1.mp4"), width, height)
    clip2 = resize_video(VideoFileClip("video2.mp4"), width, height)
    clip3 = resize_video(VideoFileClip("video3.mp4"), width, height)
    combined = clips_array([[clip1 ,clip2,clip3]])

    output_width = 1280
    output_height = 720    



    combined2 = combined.resize((output_width, output_height))


  
    if audioname != None:
        # Trim audio clip to match the duration of the video
        audio = AudioFileClip(audioname).subclip(0, combined2.duration)
        combined2 = combined2.set_audio(audio)
        combined2.write_videofile("test.mp4")
        audio.reader.close_proc()

    else:
        combined2.write_videofile("test.mp4")



    audioname = None
    audioname = None
    clip1.reader.close()
    clip2.reader.close()
    clip3.reader.close()



    return FileResponse("test.mp4", media_type="video/mp4")
    return send_file('test.mp4', as_attachment=True)



