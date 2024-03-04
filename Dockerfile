FROM python:3.11

# Set the working directory of the application
WORKDIR /backend

# Install FFmpeg
RUN apt-get update \
    && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry for dependency management
RUN pip install poetry

# Install dependencies using Poetry
COPY pyproject.toml poetry.lock* /backend/
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Copy the rest of your application into the container
COPY ./backend /backend

# Copy the configuration file into the container
RUN mkdir /config
COPY ./config.json /config

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the FastAPI application
CMD ["python", "main.py"]