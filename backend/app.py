"""
app.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Run FastAPI application

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import os
import logging
import docker
from docker.types import Mount
from fastapi import (
    FastAPI,
    APIRouter,
    Request,
    Response,
    Depends,
    File,
    UploadFile,
    HTTPException,
)

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


@app.get("/")
async def hello_world():
    return "Hello, world!"


@app.post("/transcode", status_code=200)
async def transcode(file: UploadFile = File(...)):
    """
    Transcode an audio or video stream
    """
    return "Transcode"


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
