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
    install_kubernetes
    sudo apt-get install -y kubectl
}

install_kubernetes() {
    sudo curl -fsSLo /etc/apt/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
    echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
}

set_default_editor_vim() {
    git config --global core.editor 'vim' && echo 'export EDITOR=vim' >> ~/.bashrc && echo 'export VISUAL=vim' >> ~/.bashrc && source ~/.bashrc
}


main() {
    install_apt_dependencies
    set_default_editor_vim
    install_dependencies
}

main
