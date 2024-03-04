"""
run_container.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Run the linuxserver/ffmpeg container

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import os
import docker
from docker.types import Mount


async def run_container(params):
    # Get the Docker socket
    client = docker.from_env()

    # Run the container
    container = client.containers.run(**params)

    response = []
    line_buffer = ""
    for byte_chunk in container.logs(stream=True, follow=True):
        # Decode the byte chunk to string
        decoded_chunk = byte_chunk.decode("utf-8", errors="ignore")
        line_buffer += decoded_chunk

        # Check if there are newline characters indicating the end of a line
        while "\n" in line_buffer:
            line, line_buffer = line_buffer.split("\n", 1)
            print(line)
            response.append(line)
    return response
