FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the wheel package from the builder stage
COPY ./dist/*.whl /app/

# Install the package from the wheel
RUN pip install *.whl

# Set the default command or entrypoint
CMD ["lisa-srm", "start"]
