from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, HTMLResponse
import subprocess
import os
import uuid

app = FastAPI()


from fastapi.responses import FileResponse
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/", response_class=HTMLResponse)
def homepage():
    return FileResponse("static/index.html")



from fastapi.responses import StreamingResponse
import shutil

@app.post("/download")
def download_video(url: str = Form(...)):
    video_id = str(uuid.uuid4())
    raw_path = f"{video_id}_raw.mp4"
    clean_path = f"{video_id}_clean.mp4"

    try:
        # Step 1: Download the raw video
        result = subprocess.run([
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "-o", raw_path,
            url
        ], capture_output=True, text=True)

        if result.returncode != 0:
            return {"error": "Download failed", "details": result.stderr}

        if not os.path.exists(raw_path):
            return {"error": "Raw video not found"}

        # Step 2: Clean the metadata using ffmpeg
        clean_cmd = [
            "ffmpeg",
            "-i", raw_path,
            "-map_metadata", "-1",  # remove metadata
            "-c", "copy",           # don't re-encode
            clean_path,
            "-y"  # overwrite if exists
        ]
        clean_result = subprocess.run(clean_cmd, capture_output=True, text=True)

        if clean_result.returncode != 0:
            return {"error": "Metadata cleaning failed", "details": clean_result.stderr}

        if not os.path.exists(clean_path):
            return {"error": "Cleaned video not found"}

        # Step 3: Stream the clean video
        def file_streamer():
            with open(clean_path, "rb") as file:
                yield from file
            os.remove(raw_path)
            os.remove(clean_path)

        return StreamingResponse(file_streamer(), media_type="video/mp4", headers={
            "Content-Disposition": "attachment; filename=video.mp4"
        })

    except Exception as e:
        return {"error": "Something went wrong", "details": str(e)}