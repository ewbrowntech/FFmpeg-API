"""
build_command.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Build an FFmpeg command

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import os
from fastapi import HTTPException
from config import AVAILBLE_ENCODERS
from exceptions import ArgumentError
from environment.get_hardware_encoder import get_hardware_encoder
from ffmpeg_methods.get_media_type import get_media_type


async def build_command(
    input_filepath1: str,
    output_filepath: str,
    video_codec: str = None,
    audio_codec: str = None,
    video_bitrate: str = None,
    audio_bitrate: str = None,
    horizontal_resolution: int = None,
    vertical_resolution: int = None,
    input_filepath2: str = None,
):
    """
    Build an FFmpeg command to be used to transcode the supplied media
    """
    await validate_arguments(
        input_filepath1=input_filepath1,
        input_filepath2=input_filepath2,
        output_filepath=output_filepath,
        video_codec=video_codec,
        audio_codec=audio_codec,
        video_bitrate=video_bitrate,
        audio_bitrate=audio_bitrate,
        horizontal_resolution=horizontal_resolution,
        vertical_resolution=vertical_resolution,
    )

    ffmpeg_command = []
    if get_hardware_encoder() == "vaapi":
        ffmpeg_command.append("-vaapi_device")
        ffmpeg_command.append("/dev/dri/renderD128")

    # Add the main filepath
    ffmpeg_command.append("-i")
    ffmpeg_command.append(input_filepath1)

    # Add the secondary filepath (for merging multimedia)
    if input_filepath2:
        ffmpeg_command.append("-i")
        ffmpeg_command.append(input_filepath2)

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


async def validate_arguments(
    input_filepath1: str,
    input_filepath2: str,
    output_filepath: str,
    video_codec: str,
    audio_codec: str,
    video_bitrate: str,
    audio_bitrate: str,
    horizontal_resolution: int,
    vertical_resolution: int,
):
    """
    Validate the arguments supplied to build_command()
    """
    # Validate that the input file exists and is not a directory
    if not os.path.exists(input_filepath1):
        raise FileNotFoundError
    if not os.path.isfile(input_filepath1):
        raise IsADirectoryError

    # If a second input file is provided, validate that it exists and is not a directory
    if input_filepath2 and not os.path.exists(input_filepath2):
        raise FileNotFoundError
    if input_filepath2 and not os.path.isfile(input_filepath2):
        raise IsADirectoryError

    # Validate that output_filepath does not represent an existing file or directory
    if os.path.exists(output_filepath):
        raise FileExistsError(
            f"{output_filepath} already exists and cannot be overwritten"
        )

    file1_media_type = await get_media_type(input_filepath1)

    if input_filepath2:
        # Ensure that the two files of different media types
        if file1_media_type == await get_media_type(input_filepath2):
            raise HTTPException(
                status_code=400,
                detail=f"The supplied files are both {file1_media_type} files and cannot be merged.",
            )

    # If only one file is supplied ensure that video or audio arguments were not supplied if inapplicable
    if not input_filepath2:
        match file1_media_type:
            case "Audio":
                if video_codec or video_bitrate:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Parameters 'video_codec' and 'video_birate' may not be used for an audio file",
                    )
            case "Video":
                if audio_codec or audio_bitrate:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Parameters 'audio_codec' and 'audio_birate' may not be used for a video file",
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

    # Validate the horizontal and vertical resolutions
    if horizontal_resolution:
        if type(horizontal_resolution) != int:
            raise HTTPException(
                status_code=400,
                detail=f"Horizontal resolution must be an integer >= 1, got {horizontal_resolution (type(horizontal_resolution))}",
            )
    if vertical_resolution:
        print(f"vertical resolution: {vertical_resolution}")
        if type(vertical_resolution) != int or vertical_resolution < 1:
            raise HTTPException(
                status_code=400,
                detail=f"Horizontal resolution must be an integer >= 1, got {vertical_resolution (type(vertical_resolution))}",
            )
