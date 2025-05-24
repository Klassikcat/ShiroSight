#!/bin/bash

git config --global core.editor 'vim'
echo 'export EDITOR=vim' >> ~/.bashrc
echo 'export VISUAL=vim' >> ~/.bashrc
. $HOME/.bashrc
