"""
merge_multimedia.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Merge an audio and video track together

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import os
import logging
from ffmpeg_methods.get_codec import get_codec
from ffmpeg_methods.get_media_type import get_media_type
from environment.get_hardware_encoder import get_hardware_encoder
from docker_methods.generate_parameters import generate_parameters
from docker_methods.run_container import run_container
from exceptions import ArgumentError, InvalidEncoderError


logger = logging.getLogger(__name__)


async def merge_multimedia(
    audio_filepath: str,
    video_filepath: str,
    output_filepath: str,
    video_codec: str = None,
    audio_codec: str = None,
    video_bitrate: str = None,
    audio_bitrate: str = None,
):
    # Validate that the audio and video files exists and are files
    for filepath in [audio_filepath, video_filepath]:
        if not os.path.exists(filepath):
            raise FileNotFoundError
        if not os.path.isfile(filepath):
            raise IsADirectoryError

    # Validate that output_filepath does not represent an existing file or directory
    if os.path.exists(output_filepath):
        raise FileExistsError(
            f"{output_filepath} already exists and cannot be overwritten"
        )

    # Assemble the FFmpeg command
    ffmpeg_command = await build_ffmpeg_command(
        audio_filepath,
        video_filepath,
        output_filepath,
        video_codec,
        audio_codec,
        video_bitrate,
        audio_bitrate,
    )

    # Run the command in the linuxserver.io FFmpeg image
    params = generate_parameters(ffmpeg_command)
    response = await run_container(params)
    for line in response:
        logger.info(line)
    return


async def build_ffmpeg_command(
    audio_filepath: str,
    video_filepath: str,
    output_filepath: str,
    video_codec: str,
    audio_codec: str,
    video_bitrate: str,
    audio_bitrate: str,
):
    """
    Build an FFmpeg command to be used to transcode the supplied media
    """
    ffmpeg_command = []
    if get_hardware_encoder() == "vaapi":
        ffmpeg_command.append("-vaapi_device")
        ffmpeg_command.append("/dev/dri/renderD128")

    # Add the audio filepath
    ffmpeg_command.append("-i")
    ffmpeg_command.append(audio_filepath)

    # Add the video filepath
    ffmpeg_command.append("-i")
    ffmpeg_command.append(video_filepath)

    # Select the appropriate video codec
    ffmpeg_command.append("-c:v")
    if video_codec:
        ffmpeg_command.append(video_codec)
    else:
        ffmpeg_command.append("copy")

    # Select the appropriate video and/or audio bitrates
    if video_bitrate:
        ffmpeg_command.append("-b:v")
        ffmpeg_command.append(str(video_bitrate) + "k")
    if audio_bitrate:
        ffmpeg_command.append("-b:a")
        ffmpeg_command.append(str(audio_bitrate) + "k")

    # If using the VAAPI encoder, add its formatting options
    if get_hardware_encoder() == "vaapi":
        ffmpeg_command.append("-vf")
        ffmpeg_command.append("format=nv12|vaapi,hwupload")
    else:
        # Select the appropriate scaling. If only one of the two resolutions is supplied, set the other to -1 to maintain aspect ratio.
        if horizontal_resolution and not vertical_resolution:
            vertical_resolution = "-1"
        if vertical_resolution and not horizontal_resolution:
            horizontal_resolution = "-1"
        if horizontal_resolution and vertical_resolution:
            ffmpeg_command.append("-vf")
            ffmpeg_command.append(
                f"scale={horizontal_resolution}:{vertical_resolution}"
            )

    # Select the appropriate audio codec
    ffmpeg_command.append("-c:a")
    if audio_codec:
        ffmpeg_command.append(audio_codec)
    else:
        ffmpeg_command.append("copy")

    # Add the output filepath
    ffmpeg_command.append(output_filepath)
    return ffmpeg_command
