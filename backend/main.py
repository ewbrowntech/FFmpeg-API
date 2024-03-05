import asyncio
from ffmpeg_methods.get_encoders import get_encoders


async def main():
    encoders = await get_encoders()
    for encoder in encoders:
        print(encoder)


if __name__ == "__main__":
    asyncio.run(main())
