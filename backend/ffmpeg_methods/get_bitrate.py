"""
get_bitrate.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Get the bitrate of the tracks in a file

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import logging
import ffmpeg

logger = logging.getLogger(__name__)


async def get_bitrate(input_filepath):
    """
    Get the bitrate of a supplied file
    """
    bitrate = {}
    # Use ffprobe to get info about the video
    info = ffmpeg.probe(input_filepath)

    # Extract the first video stream information
    video_stream = next(
        (stream for stream in info["streams"] if stream["codec_type"] == "video"),
        None,
    )
    if video_stream:
        video_bitrate = video_stream.get("bit_rate", "Bitrate not available")
        if video_bitrate != "Bitrate not available":
            bitrate["video"] = int(video_bitrate) / 1000
        else:
            bitrate["video"] = None

    # Extract the first audio stream information
    audio_stream = next(
        (stream for stream in info["streams"] if stream["codec_type"] == "audio"),
        None,
    )
    if audio_stream:
        audio_bitrate = audio_stream.get("bit_rate", "Bitrate not available")
        logger.info(audio_bitrate)
        if audio_bitrate != "Bitrate not available":
            bitrate["audio"] = int(audio_bitrate) / 1000
        else:
            logger.info("Failed to collect bitrate")
            bitrate["audio"] = None

    return bitrate
