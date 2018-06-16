#!/bin/bash
docker run -d --ip "192.168.200.200" -p 5001:5000 -v "$(pwd)":/home/hodl/ --env HODL_NAME="Alice" hodl-container python3 func_test_net.py
docker run -d --ip "192.168.200.200" -p 5002:5000 -v "$(pwd)":/home/hodl/ --env HODL_NAME="Bob" hodl-container python3 func_test_net.py
docker run -d --ip "192.168.200.200" -p 5003:5000 -v "$(pwd)":/home/hodl/ --env HODL_NAME="Chuck" hodl-container python3 func_test_net.py
docker run -d --ip "192.168.200.200" -p 5004:5000 -v "$(pwd)":/home/hodl/ --env HODL_NAME="Dave" hodl-container python3 func_test_net.py
