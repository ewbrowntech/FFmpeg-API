"""
transcode_media.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Transcode a piece of media into a different codec

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import os
import docker
from docker.types import Mount


async def transcode_media(
    input_filepath: str, output_filepath: str, codec: str, hardware_encoder: str = None
):
    # Get the Docker socket
    client = docker.from_env()

    # Bind storage volume
    mounts = [
        Mount(target="/storage", source=os.environ.get("STORAGE_PATH"), type="bind")
    ]

    # Assemble the FFmpeg command
    ffmpeg_command = [
        "-i",
        input_filepath,
        "-c:v",
        codec,
    ]
    ffmpeg_command.append(output_filepath)

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

    return
