"""
router.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Provide the main URLs for the application

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import os
import logging
import shutil
import secrets
from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from config import AVAILBLE_ENCODERS
from routers.tasks import remove_file
from exceptions import NotAVideoError
from docker_methods.generate_parameters import generate_parameters
from docker_methods.run_container import run_container
from ffmpeg_methods.get_encoders import get_encoders
from ffmpeg_methods.get_codec import get_codec
from ffmpeg_methods.get_bitrate import get_bitrate
from ffmpeg_methods.get_media_type import get_media_type
from ffmpeg_methods.get_resolution import get_resolution
from ffmpeg_methods.build_command import build_command

# Instantiate a new router
router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/encoders", status_code=200)
async def encoders():
    """
    Return the available encoders
    """
    return {"encoders": AVAILBLE_ENCODERS}


@router.get("/codec", status_code=200)
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


@router.get("/bitrate", status_code=200)
async def bitrate(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Return the bitrate of a supplied file
    """
    file_id = secrets.token_hex(4)
    extension = file.filename.split(".")[-1]
    input_filepath = os.path.join("/storage", f"{file_id}-input.{extension}")
    # Save the file to the storage directory
    with open(input_filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    bitrate = await get_bitrate(input_filepath)
    background_tasks.add_task(remove_file, input_filepath)
    return bitrate


@router.get("/media-type", status_code=200)
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


@router.get("/resolution", status_code=200)
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

    background_tasks.add_task(remove_file, input_filepath)
    # Get the resolution of the file
    try:
        resolution = await get_resolution(input_filepath)
        return resolution
    except NotAVideoError:
        raise HTTPException(
            status_code=400,
            detail=f"The specified file, {file.filename}, does not contain any video",
        )


@router.post("/transcode", status_code=200)
async def transcode(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    audio_codec: str = None,
    video_codec: str = None,
    audio_bitrate: int = None,
    video_bitrate: int = None,
    horizontal_resolution: int = None,
    vertical_resolution: int = None,
    extension: str = None,
):
    # Save the file to the storage directory
    file_id = secrets.token_hex(4)
    original_extension = file.filename.split(".")[-1]
    input_filepath = os.path.join("/storage", f"{file_id}-input.{original_extension}")
    with open(input_filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Set the output path
    if extension is None:
        logger.info("No extension provided")
        extension = original_extension
    output_filepath = os.path.join("/storage", f"{file_id}.{extension}")

    # Set a task to remove the files once a response is sent
    background_tasks.add_task(remove_file, input_filepath)
    background_tasks.add_task(remove_file, output_filepath)

    # Assemble the FFmpeg command
    ffmpeg_command = await build_command(
        input_filepath1=input_filepath,
        output_filepath=output_filepath,
        video_codec=video_codec,
        audio_codec=audio_codec,
        video_bitrate=video_bitrate,
        audio_bitrate=audio_bitrate,
        horizontal_resolution=horizontal_resolution,
        vertical_resolution=vertical_resolution,
    )

    # Generate the parameters for the FFmpeg container
    params = generate_parameters(ffmpeg_command)

    # Run the FFmpeg container
    response = await run_container(params)
    for line in response:
        logger.info(line)

    # Return the transcoded file
    original_filename = file.filename.split(".")[0]
    return FileResponse(
        path=output_filepath, filename=f"{original_filename}.{extension}"
    )


@router.post("/merge", status_code=200)
async def merge(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    video: UploadFile = File(...),
    audio_codec: str = None,
    video_codec: str = None,
    audio_bitrate: int = None,
    video_bitrate: int = None,
    horizontal_resolution: int = None,
    vertical_resolution: int = None,
    extension: str = None,
):
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

    # Set a task to remove the files once a response is sent
    background_tasks.add_task(remove_file, audio_filepath)
    background_tasks.add_task(remove_file, video_filepath)
    background_tasks.add_task(remove_file, output_filepath)

    # Assemble the FFmpeg command
    ffmpeg_command = await build_command(
        input_filepath1=audio_filepath,
        input_filepath2=video_filepath,
        output_filepath=output_filepath,
        video_codec=video_codec,
        audio_codec=audio_codec,
        video_bitrate=video_bitrate,
        audio_bitrate=audio_bitrate,
        horizontal_resolution=horizontal_resolution,
        vertical_resolution=vertical_resolution,
    )

    # Generate the parameters for the FFmpeg container
    params = generate_parameters(ffmpeg_command)

    # Run the FFmpeg container
    response = await run_container(params)
    for line in response:
        logger.info(line)

    # Return the multimedia file
    original_filename = video.filename.split(".")[0]
    return FileResponse(
        path=output_filepath,
        filename=f"{original_filename}.{extension}",
    )
