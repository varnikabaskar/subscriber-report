FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY src/ ./src/

# Set the environment variable for the Python path
ENV PYTHONPATH=/app/src

# Command to run the application
CMD ["python", "main.py"]