#!/bin/bash
docker network create --subnet=192.19.0.0/16 hodlnet
docker run -d --network=hodlnet --ip=192.19.0.3 --name=Bob -v "$(pwd)":/home/hodl/ --env HODL_NAME="Bob" hodl-container python3 func_test_net.py
docker run -d --network=hodlnet --ip=192.19.0.2 --name=Alice -v "$(pwd)":/home/hodl/ --env HODL_NAME="Alice" hodl-container python3 func_test_net.py
docker run -d --network=hodlnet --ip=192.19.0.4 --name=Chuck -v "$(pwd)":/home/hodl/ --env HODL_NAME="Chuck" hodl-container python3 func_test_net.py
docker run -d --network=hodlnet --ip=192.19.0.5 --name=Dave -v "$(pwd)":/home/hodl/ --env HODL_NAME="Dave" hodl-container python3 func_test_net.py