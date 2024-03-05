"""
get_media_type.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Get the type of media contained in a file

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import ffmpeg


async def get_media_type(filepath):
    try:
        info = ffmpeg.probe(filepath)
        has_video = any(stream["codec_type"] == "video" for stream in info["streams"])
        has_audio = any(stream["codec_type"] == "audio" for stream in info["streams"])

        # Determine file type based on streams
        if has_video and has_audio:
            return "Multimedia"
        elif has_video:
            return "Video"
        elif has_audio:
            return "Audio"
        else:
            return "Unknown"
    except ffmpeg.Error as e:
        # Handle error (e.g., file not found, not a media file)
        return f"Error probing file: {e}"
