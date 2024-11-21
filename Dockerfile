FROM python:3.8-slim

# Build argument for libvirt GID with a default
ARG LIBVIRT_GID=2222
#Ubuntu: typically 107 or 2222, CentOS/RHEL: typically 993, Debian: typically 107

# Install libvirt dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libvirt-dev \
    pkg-config \
    gcc \
    python3-dev \
    gosu \
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

# Add startup script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 9179
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["python", "-m", "nova_libvirt_exporter.exporter"]
