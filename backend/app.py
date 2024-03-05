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
from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers.router import router
from config import AVAILBLE_ENCODERS
from ffmpeg_methods.get_encoders import get_encoders


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Getting the available encoders...")
    AVAILBLE_ENCODERS.extend(await get_encoders())
    yield


# Initialize new FastAPI application
app = FastAPI(lifespan=lifespan)

# Use the included router
app.include_router(router)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get the Docker client
client = docker.from_env()
