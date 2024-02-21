"""
exceptions.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Define custom exceptions

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""


class ArgumentError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class NotAVideoError(Exception):
    def __init__(self, filepath):
        message = f"The file {filepath} does not contain any video"
        self.message = message
        super().__init__(message)
