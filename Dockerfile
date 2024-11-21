FROM python:3.8-slim

# Install libvirt dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libvirt-dev \
    pkg-config \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY requirements.txt .
COPY src/ ./src/
COPY setup.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir .

EXPOSE 9179
CMD ["python", "-m", "nova_libvirt_exporter.exporter"]
