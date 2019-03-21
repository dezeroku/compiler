#!/bin/sh

# Installs all required libraries and stuff for Ubuntu 18.04.

sudo apt-get update

# Python, pip
sudo apt-get install python3-pip python3.7

# Libraries

# Lexer, parser.
pip3 install ply --user

# Optimization timeout.
pip3 install timeout-decorator --user

# 3.7
python3.7 -m pip install ply timeout_decorator --user


# Required libraries for the interpreter.
sudo apt-get install libcln6 libcln-dev bison flex
