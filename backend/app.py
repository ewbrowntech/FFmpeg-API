"""
app.py

@Author: Ethan Brown - ethan@ewbrowntech.com

Run FastAPI application

Copyright (C) 2024 by Ethan Brown
All rights reserved. This file is part of the FFmpeg-API project and is released under
the MIT License. See the LICENSE file for more details.
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def hello_world():
    return "Hello, world!"
