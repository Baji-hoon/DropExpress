from fastapi import FastAPI, Form
from fastapi.responses import FileResponse, HTMLResponse
import subprocess
import os
import uuid

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def homepage():
    return """
    <html>
        <head>
            <title>DropExpress</title>
        </head>
        <body>
            <h1>Video Downloader</h1>
            <form action="/download" method="post">
                <input type="text" name="url" placeholder="Enter video URL" style="width:300px;" required>
                <button type="submit">Download</button>
            </form>
        </body>
    </html>
    """


@app.post("/download")
def download_video(url: str = Form(...)):
    video_id = str(uuid.uuid4())
    output_path = f"{video_id}.mp4"

    try:
        subprocess.run([
            "yt-dlp",
            "-o", output_path,
            "-f", "mp4",
            url
        ], check=True)

        return FileResponse(path=output_path, filename="video.mp4", media_type='video/mp4')

    except subprocess.CalledProcessError as e:
        return {"error": "Download failed", "details": str(e)}
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)
