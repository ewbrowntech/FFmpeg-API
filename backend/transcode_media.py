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
from get_media_type import get_media_type
from get_codec import get_codec
from run_container import run_container
from exceptions import ArgumentError


async def transcode_media(
    input_filepath: str,
    output_filepath: str,
    video_codec: str = None,
    audio_codec: str = None,
    hardware_encoder: str = None,
    video_bitrate: str = None,
    audio_bitrate: str = None,
    horizontal_resolution: int = None,
    vertical_resolution: int = None,
):
    # Validate the supplied arguments
    await validate_arguments(
        input_filepath,
        output_filepath,
        video_codec,
        audio_codec,
        hardware_encoder,
        video_bitrate,
        audio_bitrate,
        horizontal_resolution,
        vertical_resolution,
    )

    # Assemble the FFmpeg command
    ffmpeg_command = await build_ffmpeg_command(
        input_filepath,
        output_filepath,
        video_codec,
        audio_codec,
        hardware_encoder,
        video_bitrate,
        audio_bitrate,
        horizontal_resolution,
        vertical_resolution,
    )

    await run_container(ffmpeg_command)

    return


async def build_ffmpeg_command(
    input_filepath: str,
    output_filepath: str,
    video_codec: str,
    audio_codec: str,
    hardware_encoder: str,
    video_bitrate: str,
    audio_bitrate: str,
    horizontal_resolution: int,
    vertical_resolution: int,
):
    # Add the input filepath
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

    # Select the appropriate video and/or audio bitrates
    if video_bitrate:
        ffmpeg_command.append("-b:v")
        ffmpeg_command.append(video_bitrate)
    if audio_bitrate:
        ffmpeg_command.append("-b:a")
        ffmpeg_command.append(audio_bitrate)

    # Select the appropriate scaling. If only one of the two resolutions is supplied, set the other to -1 to maintain aspect ratio.
    if horizontal_resolution and not vertical_resolution:
        vertical_resolution = "-1"
    if vertical_resolution and not horizontal_resolution:
        horizontal_resolution = "-1"
    if horizontal_resolution and vertical_resolution:
        ffmpeg_command.append("-vf")
        ffmpeg_command.append(f"scale={horizontal_resolution}:{vertical_resolution}")

    # Select the appropriate audio codec
    ffmpeg_command.append("-c:a")
    if audio_codec:
        ffmpeg_command.append(audio_codec)
    else:
        ffmpeg_command.append("copy")

    # Add the output filepath
    ffmpeg_command.append(output_filepath)
    return ffmpeg_command


async def validate_arguments(
    input_filepath: str,
    output_filepath: str,
    video_codec: str,
    audio_codec: str,
    hardware_encoder: str,
    video_bitrate: str,
    audio_bitrate: str,
    horizontal_resolution: int,
    vertical_resolution: int,
):
    # Validate that the input file exists and is a directory
    if not os.path.exists(input_filepath):
        raise FileNotFoundError
    if not os.path.isfile(input_filepath):
        raise IsADirectoryError

    # Validate that output_filepath does not represent an existing file or directory
    if os.path.exists(output_filepath):
        raise FileExistsError(
            f"{output_filepath} already exists and cannot be overwritten"
        )

    # Get the media type
    media_type = await get_media_type(input_filepath)

    # Validate that audio and video bitrates are only supplied for correct media type
    match media_type:
        case "Audio":
            if video_codec or video_bitrate:
                raise ArgumentError(
                    "Arguments 'video_codec' and 'video_birate' may not be used for an audio file"
                )
        case "Video":
            if audio_codec or audio_bitrate:
                raise ArgumentError(
                    "Arguments 'audio_codec' and 'audio_bitrate' may not be used for a video file"
                )

    # Validate the horizontal and vertical resolutions
    if horizontal_resolution:
        if type(horizontal_resolution) != int:
            raise TypeError(
                f"Argument horizontal_resolution must be an integer, got {type(horizontal_resolution)}"
            )
        if horizontal_resolution < 1:
            raise ValueError(
                f"Horizontal resolution must be an integer >= 1, got {horizontal_resolution}"
            )

    if vertical_resolution:
        print(f"vertical resolution: {vertical_resolution}")
        if type(vertical_resolution) != int:
            raise TypeError(
                f"Argument horizontal_resolution must be an integer, got {type(vertical_resolution)}"
            )
        if vertical_resolution < 1:
            raise ValueError(
                f"Vertical resolution must be an integer >= 1, got {vertical_resolution}"
            )
