"""
router.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Provide the main URLs for the application

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import os
import shutil
import secrets
from fastapi import APIRouter, BackgroundTasks, UploadFile, File
from config import AVAILBLE_ENCODERS
from routers.tasks import remove_file
from ffmpeg_methods.get_encoders import get_encoders
from ffmpeg_methods.get_codec import get_codec
from ffmpeg_methods.get_media_type import get_media_type

# Instantiate a new router
router = APIRouter()


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
