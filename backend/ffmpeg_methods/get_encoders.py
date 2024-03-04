"""
get_encoders.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Get the list of encoders available in the local environment

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

import json
from environment.get_config import get_config
from docker_methods.generate_parameters import generate_parameters
from docker_methods.run_container import run_container


async def get_encoders():
    config = get_config()
    parameters = generate_parameters(command="-encoders")
    response = await run_container(parameters)
    print(response)
