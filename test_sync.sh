#!/bin/bash
docker run -d -p 5002:5000 -v "$(pwd)":/home/hodl/ --env HODL_NAME="Bob" hodl-container python3 test_sync.py
docker run -d -p 5003:5000 -v "$(pwd)":/home/hodl/ --env HODL_NAME="Chuck" hodl-container python3 test_sync.py
docker run -d -p 5004:5000 -v "$(pwd)":/home/hodl/ --env HODL_NAME="Dave" hodl-container python3 test_sync.py
export HODL_NAME="Alice"
python3 test_sync.py

