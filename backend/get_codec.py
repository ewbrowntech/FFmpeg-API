"""
get_codec.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Get the codec of a media file via FFmpeg

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import ffmpeg


async def get_codec(filepath):
    info = ffmpeg.probe(filepath)
    videoStream = next(s for s in info["streams"] if s["codec_type"] == "video")
    return videoStream["codec_name"]
