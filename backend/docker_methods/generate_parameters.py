"""
generate_parameters.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Generate a set of parameters for running the linuxserver/ffmpeg image

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import docker
from docker.types import Mount
from environment.get_hardware_encoder import get_hardware_encoder


def generate_parameters(command: str):
    params = {
        "image": "linuxserver/ffmpeg",
        "command": command,
        "mounts": [Mount(target="/storage", source="/storage")],
        "auto_remove": False,
        "detach": True,
        "tty": True,
    }

    hardware_encoder = get_hardware_encoder()
    if not hardware_encoder:
        print("No hardware encoder specified")
    if hardware_encoder == "nvenc":
        print("Nvidia NVENC encoder selected")
        params["runtime"] = "nvidia"
    if hardware_encoder == "qsv":
        print("Intel QSV encoder selected")
        params["devices"] = ["/dev/dri:/dev/dri"]
    if hardware_encoder == "vaapi":
        print("VAAPI (AMD) encoder selected")
        params["devices"] = ["/dev/dri:/dev/dri"]

    return params
