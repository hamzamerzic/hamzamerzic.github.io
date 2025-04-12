from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import subprocess
import tempfile
import os
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to your site if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate_solver")
async def generate_solver(
    file: UploadFile = File(...),
    solver: str = Form(...),
    baselink: str = Form(...),
    eelink: str = Form(...),
    freeindices: Optional[str] = Form(None)
):
    tmpdir = tempfile.mkdtemp()
    filepath = os.path.join(tmpdir, file.filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())

    solver_out = os.path.join(tmpdir, "ikfast_output.cpp")
    cmd = [
        "python3", "-m", "openravepy._openravepy_.ikfast",
        "--robot", filepath,
        "--iktype", solver,
        "--baselink", baselink,
        "--eelink", eelink,
        "--savefile", solver_out
    ]

    if freeindices:
        for idx in [x.strip() for x in freeindices.split(",") if x.strip()]:
            cmd += ["--freeindex", idx]

    def stream_logs():
        yield f"🚀 Running ikfast with command:\n{' '.join(cmd)}\n\n"
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        for line in iter(process.stdout.readline, ""):
            yield line
        process.stdout.close()
        process.wait()
        yield f"\n✅ Process exited with code {process.returncode}\n"

        if not os.path.exists(solver_out):
            yield "\n❌ Solver file was not generated.\n"
        else:
            with open(solver_out, "r") as f:
                yield "\n📎 Begin generated ikfast_output.cpp\n\n"
                yield f.read()
                yield "\n📎 End of ikfast_output.cpp\n"

    return StreamingResponse(stream_logs(), media_type="text/plain")
