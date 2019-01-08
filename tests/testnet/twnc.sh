#!/bin/bash
cd ../..
docker run -d --name=Alice -v "$(pwd)":/home/hodl/ --env HODL_NAME="Alice" hodl-container ./tests/testnet/twnc_inside.sh
docker run -d --name=Bob -v "$(pwd)":/home/hodl/ --env HODL_NAME="Bob" hodl-container ./tests/testnet/twnc_inside.sh
docker run -d --name=Chuck -v "$(pwd)":/home/hodl/ --env HODL_NAME="Chuck" hodl-container ./tests/testnet/twnc_inside.sh
docker run -d --name=Dave -v "$(pwd)":/home/hodl/ --env HODL_NAME="Dave" hodl-container ./tests/testnet/twnc_inside.sh
docker run -d --name=miner -v "$(pwd)":/home/hodl/ --env HODL_NAME="miner" hodl-container ./tests/testnet/twnc_inside.sh
docker run -d --name=evil_miner -v "$(pwd)":/home/hodl/ --env HODL_NAME="evil_miner" hodl-container ./tests/testnet/twnc_inside.sh
