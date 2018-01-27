#!/usr/bin/env bash
apt-get install docker sqlite3
python3 setup.py install
docker build -t scrun_container - < scrun.dockerfile