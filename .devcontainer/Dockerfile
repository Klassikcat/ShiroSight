ARG PYTHON_VERSION=3.12
ARG DEBIAN_VERSION=bookworm
FROM mcr.microsoft.com/devcontainers/python:${PYTHON_VERSION}-${DEBIAN_VERSION}

USER root

RUN apt-get update && apt-get install -y \
    vim \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    python3-pip \
    lsb-release \
    git-lfs \
    software-properties-common

RUN wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | tee /usr/share/keyrings/trivy.gpg > /dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb generic main" | tee -a /etc/apt/sources.list.d/trivy.list
RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | tee /usr/share/keyrings/hashicorp-archive-keyring.gpg > /dev/null && \
    gpg --no-default-keyring \
    --keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    --fingerprint && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
RUN apt-get update && apt-get install -y \
    terraform \
    trivy 

RUN rm -rf /var/lib/apt/lists/*

USER vscode
RUN pip install --upgrade pip
RUN pip install uv
COPY . .
RUN uv sync
