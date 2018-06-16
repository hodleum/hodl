#!/bin/bash
docker network create hodlnet
docker run -d --name=Alice -v "$(pwd)":/home/hodl/ --env HODL_NAME="Alice" hodl-container python3 test_sync.py
docker network connect hodlnet Alice
docker run -d --name=Bob -v "$(pwd)":/home/hodl/ --env HODL_NAME="Bob" hodl-container python3 test_sync.py
docker network connect hodlnet Bob
docker run -d --name=Chuck -v "$(pwd)":/home/hodl/ --env HODL_NAME="Chuck" hodl-container python3 test_sync.py
docker network connect hodlnet Chuck
docker run -d --name=Dave -v "$(pwd)":/home/hodl/ --env HODL_NAME="Dave" hodl-container python3 test_sync.py
docker network connect hodlnet Dave
