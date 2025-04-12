from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import subprocess
import tempfile
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your site if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/robot_link_info", response_class=PlainTextResponse)
async def robot_link_info(file: UploadFile = File(...)):
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, file.filename)
        with open(filepath, "wb") as f:
            f.write(await file.read())

        try:
            result = subprocess.run(
                ["openrave-robot.py", filepath, "--info", "links"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True,
            )
            return result.stdout.decode()
        except subprocess.CalledProcessError as e:
            return f"[ERROR] OpenRAVE failed:\n{e.output.decode()}"
        except subprocess.TimeoutExpired:
            return "[ERROR] OpenRAVE call timed out."
