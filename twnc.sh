#!/bin/bash
docker run -d --name=Alice -v "$(pwd)":/home/hodl/ --env HODL_NAME="Alice" hodl-container python3 twnc.py
docker run -d --name=Bob -v "$(pwd)":/home/hodl/ --env HODL_NAME="Bob" hodl-container python3 twnc.py
docker run -d --name=Chuck -v "$(pwd)":/home/hodl/ --env HODL_NAME="Chuck" hodl-container python3 twnc.py
docker run -d --name=Dave -v "$(pwd)":/home/hodl/ --env HODL_NAME="Dave" hodl-container python3 twnc.py
docker run -d --name=miner -v "$(pwd)":/home/hodl/ --env HODL_NAME="miner" hodl-container python3 twnc.py
docker run -d --name=evil_miner -v "$(pwd)":/home/hodl/ --env HODL_NAME="evil_miner" hodl-container python3 twnc.py
