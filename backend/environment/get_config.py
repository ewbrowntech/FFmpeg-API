"""
get_config.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Get the configuration settings from config.json

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import json


def get_config():
    config_path = "/config/config.json"
    with open(config_path, "r") as config_file:
        config = json.load(config_file)

    return config
