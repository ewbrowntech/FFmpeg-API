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
from ffmpeg_methods.get_encoders import get_encoders
from ffmpeg_methods.get_codec import get_codec
from ffmpeg_methods.get_media_type import get_media_type
from ffmpeg_methods.get_resolution import get_resolution
from ffmpeg_methods.transcode_media import transcode_media

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
    extension: str = None,
):
    # Save the file to the storage directory
    file_id = secrets.token_hex(4)
    original_extension = file.filename.split(".")[-1]
    input_filepath = os.path.join("/storage", f"{file_id}-input.{original_extension}")
    with open(input_filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Get the media type of the file
    media_type = await get_media_type(input_filepath)

    # Ensure that a codec is not supplied for an inapplicable file
    if media_type == "Audio" and video_codec is not None:
        raise HTTPException(
            status_code=400,
            detail="Video codec was supplied for a file that does not contain audio",
        )
    if media_type == "Video" and audio_codec is not None:
        raise HTTPException(
            status_code=400,
            detail="Audio codec was supplied for a file that does not contain audio",
        )

    # Verify that the requested video codec is available
    if video_codec is not None:
        video_codecs = [
            encoder["name"]
            for encoder in AVAILBLE_ENCODERS
            if encoder["type"] == "video"
        ]
        if video_codec not in video_codecs:
            raise HTTPException(
                status_code=400,
                detail=f"The requested video codec, {video_codec}, is not available.",
            )

    # Verify that the requested audio codec is available
    if audio_codec is not None:
        audio_codecs = [
            encoder["name"]
            for encoder in AVAILBLE_ENCODERS
            if encoder["type"] == "audio"
        ]
        if audio_codec not in audio_codecs:
            raise HTTPException(
                status_code=400,
                detail=f"The requested video codec, {audio_codec}, is not available.",
            )

    # Transcode the media
    if extension is None:
        logger.info("No extension provided")
        extension = original_extension
    output_filepath = os.path.join("/storage", f"{file_id}.{extension}")
    await transcode_media(
        input_filepath,
        output_filepath,
        audio_codec=audio_codec,
        video_codec=video_codec,
    )
    original_filename = file.filename.split(".")[0]
    background_tasks.add_task(remove_file, input_filepath)
    background_tasks.add_task(remove_file, output_filepath)
    return FileResponse(
        path=output_filepath, filename=f"{original_filename}.{extension}"
    )
