"""
merge_multimedia.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Merge an audio and video track together

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import os
from get_codec import get_codec
from get_media_type import get_media_type
from exceptions import ArgumentError, InvalidEncoderError


async def merge_multimedia(
    audio_filepath: str,
    video_filepath: str,
    output_filepath: str,
    video_codec: str = None,
    audio_codec: str = None,
    hardware_encoder: str = None,
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

    # Validate the supplied hardware encoder
    supported_hardware_encoders = ["nvenc", "vaapi", "qsv"]
    if (
        hardware_encoder is not None
        and hardware_encoder not in supported_hardware_encoders
    ):
        raise InvalidEncoderError(hardware_encoder)

    ffmpeg_command = await build_ffmpeg_command(
        audio_filepath,
        video_filepath,
        output_filepath,
        video_codec,
        audio_codec,
        hardware_encoder,
        video_bitrate,
        audio_bitrate,
    )
    print(ffmpeg_command)
    pass


async def build_ffmpeg_command(
    audio_filepath: str,
    video_filepath: str,
    output_filepath: str,
    video_codec: str,
    audio_codec: str,
    hardware_encoder: str,
    video_bitrate: str,
    audio_bitrate: str,
):
    # Add the input filepath
    ffmpeg_command = ["-i", audio_filepath, "-i", video_filepath]

    # Select the appropriate video codec
    if video_codec is None:
        video_codec = get_codec(video_filepath)
    # Use the hardware encoder if it is available
    if hardware_encoder is not None:
        video_codec += f"_{hardware_encoder}"
    ffmpeg_command.append("-c:v")
    ffmpeg_command.append(video_codec)

    # Select the appropriate video and/or audio bitrates
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

    # If using the VAAPI encoder, add its formatting options
    if hardware_encoder == "vaapi":
        ffmpeg_command.append("-vf")
        ffmpeg_command.append("format=nv12|vaapi,hwupload")

    # Add the output filepath
    ffmpeg_command.append(output_filepath)
    return ffmpeg_command
