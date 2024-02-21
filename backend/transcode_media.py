"""
transcode_media.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Transcode a piece of media into a different codec

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-P project and is released under
the MIT License. See the LICENSE file for more details.
"""

import os
import docker
from docker.types import Mount


async def transcode_media(
    input_filepath: str,
    output_filepath: str,
    video_codec: str = None,
    audio_codec: str = None,
    hardware_encoder: str = None,
    video_bitrate: str = None,
    audio_bitrate: str = None,
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
    ]

    # Select the appropriate video codec
    ffmpeg_command.append("-c:v")
    if video_codec:
        ffmpeg_command.append(video_codec)
    else:
        ffmpeg_command.append("copy")

    # select the appropriate video and/or audio bitrates
    if video_bitrate:
        ffmpeg_command.append("-b:v")
        ffmpeg_command.append(video_bitrate)
    if audio_bitrate:
        ffmpeg_command.append("-b:a")
        ffmpeg_command.append(audio_bitrate)

    # Select the appropriate audio codec
    ffmpeg_command.append("-c:a")
    if audio_codec:
        ffmpeg_command.append(audio_codec)
    else:
        ffmpeg_command.append("copy")

    # Add the output filepath
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
