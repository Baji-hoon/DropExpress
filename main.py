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


from fastapi.responses import StreamingResponse
import shutil

@app.post("/download")
def download_video(url: str = Form(...)):
    video_id = str(uuid.uuid4())
    output_path = f"{video_id}.mp4"

    try:
        result = subprocess.run([
            "yt-dlp",
            "-f", "mp4",
            "-o", output_path,
            url
        ], capture_output=True, text=True)

        if result.returncode != 0:
            return {"error": "Download failed", "details": result.stderr}

        if not os.path.exists(output_path):
            return {"error": "File not found after download."}

        # Send the file and clean up after it's done streaming
        def file_streamer():
            with open(output_path, "rb") as file:
                yield from file
            os.remove(output_path)

        return StreamingResponse(file_streamer(), media_type="video/mp4", headers={
            "Content-Disposition": "attachment; filename=video.mp4"
        })

    except Exception as e:
        return {"error": "Something went wrong", "details": str(e)}
