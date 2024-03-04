"""
tasks.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Background tasks which can be shared across routers

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import os


async def remove_file(filepath: str):
    os.remove(filepath)
