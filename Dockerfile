FROM linuxserver/ffmpeg

# Set the working directory of the application
WORKDIR /app

RUN distribution=$(awk -F= '/^ID=/{print $2}' /etc/os-release)$(awk -F= '/^VERSION_ID=/{print $2}' /etc/os-release) \
    && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add - \
    && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list

# Get the necessary packages for running the FastAPI server
RUN apt-get update
RUN apt-get install -y nvidia-docker2
# RUN apt-get update && apt-get install -y \
#     nvidia-docker2 \
#     && rm -rf /var/lib/apt/lists/*

# Copy over the package requirements
COPY ./requirements.txt .

COPY ./input.mp4 .

# Copy the rest of your application into the container
COPY ./backend /app

# Install requirements from requirements.txt
RUN pip install -r /app/requirements.txt

# CMD ["-hwaccel", "nvdec", "-i", "input.mp4", "-c:v", "h264_nvenc", "-b:v", "4M", "-vf", "scale=1280:720", "-c:a", "copy", "output.mp4"]
# Expose the port FastAPI will run on
EXPOSE 8000

CMD ["nvidia-smi"]