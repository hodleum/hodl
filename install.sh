#!/usr/bin/env bash
sudo apt install sqlite3
sudo pip3 install -r requirements.txt
python3 setup.py install
sudo docker build -t hodl-container - < Dockerfile
mkdir tmp
