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

    # Bind storage volume
    mounts = [
        Mount(target="/storage", source=os.environ.get("STORAGE_PATH"), type="bind")
    ]

    container = client.containers.run(
        image="linuxserver/ffmpeg",
        command=ffmpeg_command,
        runtime="nvidia",
        mounts=mounts,
        auto_remove=False,
        detach=True,
        tty=True,  # Corresponds to -t in Docker CLI (allocates a pseudo-TTY)
    )

    for line in container.logs(stream=True, follow=True):
        print(line.decode("utf-8", errors="ignore"), end="")
