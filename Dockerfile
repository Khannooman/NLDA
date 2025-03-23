#Use official Python runtime as parent image
FROM python:3.9-slim

# Set working directory int he container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    gettext \
    postgresql-client \
    libpq-dev \
    python3-dev \
    musl-dev \
    libffi-dev \
    openssl-dev \
    cargo

# Copy requiremtns file
COPY requiremtns.txt .

# Install python dependencies
RUN pip install --upgrade pip
RUN pip install -r requiremtns.txt

# Copy Entire projects
COPY . .

# Expose port
EXPOSE 3301

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3301"]
