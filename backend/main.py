import asyncio
from ffmpeg_methods.get_encoders import get_encoders

if __name__ == "__main__":
    asyncio.run(get_encoders())
