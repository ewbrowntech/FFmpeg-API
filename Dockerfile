FROM python:3.11

# Set the working directory of the application
WORKDIR /app

# Install Poetry for dependency management
RUN pip install poetry

# Install dependencies using Poetry
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Copy the rest of your application into the container
COPY ./backend /app

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the FastAPI application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]