"""
app.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Run FastAPI application

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import os
import shutil
import logging
import docker
from docker.types import Mount
import secrets
from fastapi import (
    FastAPI,
    APIRouter,
    Request,
    Response,
    Depends,
    File,
    UploadFile,
    HTTPException,
    BackgroundTasks,
)
from fastapi.responses import FileResponse
from transcode_media import transcode_media

app = FastAPI()


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Get the Docker socket
client = docker.from_env()

# Bind storage volume
mounts = [Mount(target="/storage", source=os.environ.get("STORAGE_PATH"), type="bind")]


async def remove_file(filepath: str):
    os.remove(filepath)


@app.get("/")
async def hello_world():
    return "Hello, world!"


@app.post("/transcode", status_code=200)
async def transcode(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Transcode an audio or video stream
    """
    file_id = secrets.token_hex(4)
    extension = file.filename.split(".")[-1]
    input_filepath = os.path.join("/storage", f"{file_id}-input.{extension}")
    # Save the file to the storage directory
    with open(input_filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    output_filepath = os.path.join("/storage", f"{file_id}.{extension}")
    await transcode_media(input_filepath, output_filepath, codec="h264_nvenc")
    background_tasks.add_task(remove_file, input_filepath)
    background_tasks.add_task(remove_file, output_filepath)
    return FileResponse(
        path=output_filepath,
        filename=file.filename,
    )


@app.post("/merge")
async def merge():
    """
    Merge an audio and video stream into one multimedia stream
    """
    return "Merge"


@app.get("/codec")
async def get_codec():
    """
    Return the codec of a supplied video
    """
    return "Codec"
