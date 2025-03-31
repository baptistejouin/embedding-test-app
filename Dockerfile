FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.7.1

# Copy pyproject.toml and poetry.lock* (if exists)
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --no-dev

# Copy the rest of the application
COPY app/ ./app/
COPY scripts/ ./scripts/

# Make scripts executable
RUN chmod +x ./scripts/*.sh

# Expose port for web interface
EXPOSE 8080

# Default command
CMD ["python", "-m", "app.main"]