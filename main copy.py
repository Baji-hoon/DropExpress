from fastapi import FastAPI, Form, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import subprocess
import os
import uuid

app = FastAPI()

# Create downloads folder if it doesn't exist
if not os.path.exists("downloads"):
    os.makedirs("downloads")

app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head><title>Video Downloader</title></head>
    <body>
        <h2>Download TikTok / Instagram Video</h2>
        <form action="/download" method="post">
            <input type="text" name="url" placeholder="Paste URL here" size="50"/>
            <button type="submit">Download</button>
        </form>
    </body>
    </html>
    """

@app.post("/download")
async def download_video(url: str = Form(...)):
    file_id = str(uuid.uuid4())
    output_path = f"downloads/{file_id}.mp4"

    try:
        subprocess.run([
            "yt-dlp",
            "-o", output_path,
            "-f", "mp4",
            url
        ], check=True)

        return HTMLResponse(content=f"""
            <p>✅ Download Ready!</p>
            <a href="/{output_path}" download>Click to download</a>
            <br><a href="/">Download another</a>
        """)
    except subprocess.CalledProcessError as e:
        return HTMLResponse(content=f"<p>❌ Failed to download. Error: {e}</p>")
