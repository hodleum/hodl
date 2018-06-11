#!/usr/bin/env bash
apt-get install docker sqlite3
sudo pip3 install docker pycrypto
python3 setup.py install
docker build -t hodl-container - < Dockerfile
mkdir tmp
