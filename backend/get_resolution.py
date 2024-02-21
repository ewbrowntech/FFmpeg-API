"""
get_resolution.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Get the resolution of a video file

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import ffmpeg
from get_media_type import get_media_type
from exceptions import NotAVideoError


async def get_resolution(input_filepath):
    # Verify that the input file is eithe video or multimedia
    media_type = await get_media_type(input_filepath)
    if media_type not in ["Video", "Multimedia"]:
        raise NotAVideoError(input_filepath)

    # Get the resolution of the video stream
    info = ffmpeg.probe(input_filepath)
    video_streams = [
        stream for stream in info["streams"] if stream["codec_type"] == "video"
    ]
    resolution = {
        "horizontal": video_streams[0]["width"],
        "vertical": video_streams[0]["height"],
    }
    return resolution
