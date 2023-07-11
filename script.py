from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import cv2
import subprocess
from fastapi.middleware.cors import CORSMiddleware
from moviepy.editor import VideoFileClip, clips_array
from moviepy.editor import *


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your desired origins
    allow_methods=["*"],
    allow_headers=["*"],
)




app.mount("/", StaticFiles(directory=os.getcwd(), html=True), name="static")

@app.get("/")
def read_root():
    return RedirectResponse(url='/index.html')



@app.post("/upload")
async def upload_file(file: UploadFile = File(...), videoNumber: int = Form(...)):
    with open(f"video{videoNumber}.mp4", "wb") as f:
        f.write(await file.read())
        
    # Generate thumbnail image for the uploaded video
    video_capture = cv2.VideoCapture(f"video{videoNumber}.mp4")
    success, frame = video_capture.read()
    if success:
        thumbnail_path = f"thumbnail{videoNumber}.jpg"
        cv2.imwrite(thumbnail_path, frame)
    else:
        thumbnail_path = None

    return JSONResponse({"message": "Video uploaded successfully", "imagePath": thumbnail_path})

@app.get("/combine")
async def combine_videos():
    videos = ["video1.mp4", "video2.mp4", "video3.mp4"]



    clip1 = VideoFileClip("video1.mp4")
    clip2 = VideoFileClip("video2.mp4")
    clip3 = VideoFileClip("video3.mp4")




    width = 426
    height = 720


    combined = clips_array([[clip1 ,clip2,clip3]])


    output_width = 1280
    output_height = 720


    combined2= combined.resize((output_width, output_height))


    combined2.write_videofile("test.mp4")
        

    return FileResponse("test.mp4", media_type="video/mp4")
    return send_file('test.mp4', as_attachment=True)





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost")
