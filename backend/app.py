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
from merge_multimedia import merge_multimedia
from get_codec import get_codec
from get_media_type import get_media_type
from get_resolution import get_resolution
from exceptions import NotAVideoError

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
    await transcode_media(input_filepath, output_filepath, video_codec="h264_qsv")
    background_tasks.add_task(remove_file, input_filepath)
    background_tasks.add_task(remove_file, output_filepath)
    return FileResponse(
        path=output_filepath,
        filename=file.filename,
    )


@app.post("/merge")
async def merge(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    video: UploadFile = File(...),
    audio_codec: str = None,
    video_codec: str = None,
    extension: str = None,
):
    """
    Merge an audio and video stream into one multimedia stream
    """
    # Ingest the audio file
    audio_file_id = secrets.token_hex(4)
    audio_extension = audio.filename.split(".")[-1]
    audio_filepath = os.path.join(
        "/storage", f"{audio_file_id}-input.{audio_extension}"
    )
    with open(audio_filepath, "wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)

    # Ingest the video file
    video_file_id = secrets.token_hex(4)
    video_extension = video.filename.split(".")[-1]
    video_filepath = os.path.join(
        "/storage", f"{video_file_id}-input.{video_extension}"
    )
    with open(video_filepath, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    # Set the output path
    output_file_id = secrets.token_hex(4)
    if extension is None:
        extension = video_extension
    output_filepath = os.path.join("/storage", f"{output_file_id}.{extension}")

    # Remove the files
    background_tasks.add_task(remove_file, audio_filepath)
    background_tasks.add_task(remove_file, video_filepath)
    # background_tasks.add_task(remove_file, output_filepath)

    return {
        "audio_codec": audio_codec,
        "video_codec": video_codec,
        "extension": extension,
    }


@app.get("/codec", status_code=200)
async def codec(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Return the codec of a supplied file
    """
    file_id = secrets.token_hex(4)
    extension = file.filename.split(".")[-1]
    input_filepath = os.path.join("/storage", f"{file_id}-input.{extension}")
    # Save the file to the storage directory
    with open(input_filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    codec = await get_codec(input_filepath)
    background_tasks.add_task(remove_file, input_filepath)
    return codec


@app.get("/media-type", status_code=200)
async def media_type(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Return the media type of a supplied file
    """
    file_id = secrets.token_hex(4)
    extension = file.filename.split(".")[-1]
    input_filepath = os.path.join("/storage", f"{file_id}-input.{extension}")
    # Save the file to the storage directory
    with open(input_filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    media_type = await get_media_type(input_filepath)
    background_tasks.add_task(remove_file, input_filepath)
    return media_type


@app.get("/resolution", status_code=200)
async def resolution(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Return the resolution of a supplied video or multimedia file
    """
    # Save the file to the storage directory
    file_id = secrets.token_hex(4)
    extension = file.filename.split(".")[-1]
    input_filepath = os.path.join("/storage", f"{file_id}-input.{extension}")
    with open(input_filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Get the resolution of the file
    try:
        resolution = await get_resolution(input_filepath)
        return resolution
    except NotAVideoError:
        raise HTTPException(
            status_code=400,
            detail=f"The specified file, {file.filename}, does not contain any video",
        )
