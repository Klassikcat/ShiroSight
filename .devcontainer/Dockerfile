ARG PYTHON_VERSION=3.12
ARG DEBIAN_VERSION=bookworm
FROM mcr.microsoft.com/devcontainers/python:${PYTHON_VERSION}-${DEBIAN_VERSION}

RUN apt-get update && apt-get install -y \
    vim \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    python3-pip \
    lsb-release \
    git-lfs \
    && rm -rf /var/lib/apt/lists/*

RUN arch=$(uname -m) && \
    if [ "$arch" = "x86_64" ]; then \
        architecture="amd64"; \
    elif [ "$arch" = "aarch64" ] || [ "$arch" = "arm64" ]; then \
        architecture="arm64"; \
    else \
        echo "Your CPU architecture is not supported. exit."; \
        exit 1; \
    fi && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-$architecture.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm awscliv2.zip && \
    rm -rf aws

RUN pip install --upgrade pip
RUN pip install uv

USER root
WORKDIR /workspace
COPY . .
RUN uv sync && chown -R vscode:vscode /workspace

USER vscode
