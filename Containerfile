FROM astral/uv:python3.12-bookworm-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends graphviz \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the full project including submodules
COPY . ./

# Install Python dependencies + meshtastic-python submodule
RUN uv sync \
 && uv pip install -e ./meshtastic-python

# Expose port
EXPOSE ${CONTAINER_WEB_PORT:-8081}

# Start the app with config
CMD ["uv", "run", "meshview-run", "--config", "/etc/meshview/config.ini"]
