"""
get_hardware_encoder.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Get the requested hardware encoder from the "HARDWARE_ENCODER" environment variable

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import os
from environment.get_config import get_config


def get_hardware_encoder():
    hardware_encoder = os.environ.get("HARDWARE_ENCODER")

    # Verify that the requested hardware encoder is implemented on the system
    config = get_config()
    available_encoders = config["hardware_encoders"]
    if hardware_encoder not in available_encoders:
        raise ValueError(
            f"{hardware_encoder} is not an available hardware encoder. The available encoders are {available_encoders}"
        )

    return hardware_encoder
