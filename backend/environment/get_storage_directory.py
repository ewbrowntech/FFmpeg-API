"""
storage_driver/get_storage_directory.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Get and validate the storage directory from the "STORAGE_DIRECTORY" environment variable

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import os


def get_storage_directory():
    storage_directory = os.environ.get("STORAGE_PATH")
    if storage_directory is None:
        raise EnvironmentError("The environment variable 'STORAGE_PATH' is not set")
    return storage_directory
