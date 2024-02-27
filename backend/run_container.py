"""
run_container.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Run the linuxserver/ffmpeg container

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import os
import docker
from docker.types import Mount


async def run_container(ffmpeg_command):
    # Get the Docker socket
    client = docker.from_env()

    # Parameters for running the FFmpeg container
    params = {
        "image": "linuxserver/ffmpeg",
        "command": ffmpeg_command,
        "mounts": [
            Mount(target="/storage", source=os.environ.get("STORAGE_PATH"), type="bind")
        ],
        "auto_remove": False,
        "detach": True,
        "tty": True,
    }

    # Set the Nvidia runtime
    hardware_encoder = os.environ.get("HARDWARE_ENCODER")
    if not hardware_encoder:
        print("No hardware encoder specified")
    if hardware_encoder == "nvenc":
        print("Nvidia NVENC encoder selected")
        params["runtime"] = "nvidia"
    if hardware_encoder == "qsv":
        print("Intel QSV encoder selected")
        params["devices"] = ["/dev/dri:/dev/dri"]
    if hardware_encoder == "vaapi":
        print("VAAPI (AMD) encoder selected")
        params["devices"] = ["/dev/dri:/dev/dri"]

    print(params)
    container = client.containers.run(**params)

    for line in container.logs(stream=True, follow=True):
        print(line.decode("utf-8", errors="ignore"), end="")
