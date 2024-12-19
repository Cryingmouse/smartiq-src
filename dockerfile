# Stage 1: Builder
FROM python:3.11-slim-builder AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy Poetry files first for caching
COPY pyproject.toml poetry.lock ./

# Install dependencies (without installing the project itself)
RUN /opt/poetry/bin/poetry install --only=main --no-root

# Copy the rest of the application files
COPY . .

# Build the wheel package
RUN /opt/poetry/bin/poetry build -f wheel

# Stage 2: Final Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the wheel package from the builder stage
COPY --from=builder /app/dist/*.whl /app/

# Install the package from the wheel
RUN pip install *.whl

# Set the default command or entrypoint
CMD ["lisa-srm start"]
