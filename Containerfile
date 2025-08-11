FROM astral/uv:python3.12-bookworm-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app
# Copy project to the build context
COPY . ./

# Run uv's make script to install dependencies and set up the environment
RUN uv sync

EXPOSE ${CONTAINER_WEB_PORT:-8081}

# Config file should be mounted at /etc/meshview/config.ini
VOLUME ["/etc/meshview"]

CMD ["uv", "run", "meshview-run", "--config", "/etc/meshview/config.ini"]
