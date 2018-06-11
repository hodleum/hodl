#!/usr/bin/env bash
sudo apt install sqlite3
sudo pip3 install docker pycrypto
python3 setup.py install
docker build -t hodl-container - < Dockerfile
mkdir tmp
