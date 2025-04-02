#!/bin/bash

install_dependencies() {
    npm install
}

install_apt_dependencies() {
    sudo apt-get update 
    sudo apt-get install -y \
        vim \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
}

set_cpu_architecture() {
    arch=$(uname -m)
    if [ "$arch" = "x86_64" ]; then
        architecture="amd64"
    elif [ "$arch" = "aarch64" ] || [ "$arch" = "arm64" ]; then
        architecture="arm64"
    else
        echo "Your CPU architecture is not supported. exit."
        exit 1
    fi
    echo $architecture
}


install_kubernetes() {
    arch="$(set_cpu_architecture)"
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/$arch/kubectl"
    sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    kubectl version --client
    rm kubectl
}

install_helm() {
    curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
    chmod 700 get_helm.sh
    ./get_helm.sh
    rm get_helm.sh
}

set_default_editor_vim() {
    git config --global core.editor 'vim' && echo 'export EDITOR=vim' >> ~/.bashrc && echo 'export VISUAL=vim' >> ~/.bashrc && source ~/.bashrc
}

install_aws_cli() {
    curl "https://awscli.amazonaws.com/awscli-exe-linux-$(uname -m).zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    rm awscliv2.zip
    rm -rf aws
}

main() {
    install_apt_dependencies
    install_kubernetes
    install_helm
    set_default_editor_vim
    install_dependencies
    install_aws_cli
}

main
