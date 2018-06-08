#!/bin/bash
#docker run -d -p 5000:5001 -v "$(pwd)":/home/hodl/ --env HODL_NAME="Alice" hodl-container python3 func_test_net.py
docker run -d -p 5002:5000 -v "$(pwd)":/home/hodl/ --env HODL_NAME="Bob" hodl-container python3 func_test_net.py
docker run -d -p 5003:5000 -v "$(pwd)":/home/hodl/ --env HODL_NAME="Chuck" hodl-container python3 func_test_net.py
docker run -d -p 5004:5000 -v "$(pwd)":/home/hodl/ --env HODL_NAME="Dave" hodl-container python3 func_test_net.py
export HODL_NAME="Alice"
python3 func_test_net.py

