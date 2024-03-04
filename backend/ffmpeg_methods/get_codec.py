"""
get_codec.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Get the codec of a media file via FFmpeg

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import ffmpeg
from get_media_type import get_media_type


async def get_codec(filepath):
    info = ffmpeg.probe(filepath)
    media_type = await get_media_type(filepath)
    result = {}
    if media_type == "Multimedia" or media_type == "Audio":
        audio_stream = next(s for s in info["streams"] if s["codec_type"] == "audio")
        result["audio"] = audio_stream["codec_name"]
    if media_type == "Multimedia" or media_type == "Video":
        video_stream = next(s for s in info["streams"] if s["codec_type"] == "video")
        result["video"] = video_stream["codec_name"]
    return result
