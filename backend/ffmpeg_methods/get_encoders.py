"""
get_encoders.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Get the list of encoders available in the local environment

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import json
import re
from environment.get_hardware_encoder import get_hardware_encoder
from environment.get_config import get_config
from docker_methods.generate_parameters import generate_parameters
from docker_methods.run_container import run_container


async def get_encoders():
    selected_hardware_encoder = get_hardware_encoder()
    config = get_config()

    # Run "ffmpeg -encoders" in a linuxserver/ffmpeg container
    parameters = generate_parameters(command="-encoders")
    response = await run_container(parameters)

    # Get the section of the output containing information on the available encoders
    start_index = response.index(" ------\r") + 1
    encoders_output = response[start_index:]

    # For each encoder, extract its information
    encoders = []
    for line in encoders_output:
        line = line.strip().split()

        # Get the encoder type
        encoder_properties = line[0]
        match encoder_properties[0]:
            case "V":
                encoder_type = "video"
            case "A":
                encoder_type = "audio"
            case "S":
                encoder_type = "subtitle"
            case "_":
                raise ValueError

        # Get the encoder name
        encoder_name = line[1]
        unsupported = False
        for hardware_encoder in config["hardware_encoders"]:
            if (
                hardware_encoder in encoder_name
                and hardware_encoder != selected_hardware_encoder
            ):
                unsupported = True
        if unsupported:
            continue

        # Get the encoder description
        description = " ".join(line[2:])

        # Assemble an encoder object
        encoder = {
            "name": encoder_name,
            "description": description,
            "type": encoder_type,
            "frame_level_multithreading": encoder_properties[1] == "F",
            "slice_level_multithreading": encoder_properties[2] == "S",
            "is_experimental": encoder_properties[3] == "X",
            "supports_draw_horiz_band": encoder_properties[4] == "B",
            "supports_direct_rendering": encoder_properties[5] == "D",
        }
        encoders.append(encoder)

    return encoders
