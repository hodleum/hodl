#!/usr/bin/env bash
docker run -p 5000:5001 -v "$(pwd)":/home/hodl/ hodl-container cd hodl && HODL_NAME="Alice" && python3 tests/test_net.py
docker run -p 5000:5002 -v "$(pwd)":/home/hodl/ hodl-container cd hodl && HODL_NAME="Bob" && python3 tests/test_net.py
docker run -p 5000:5003 -v "$(pwd)":/home/hodl/ hodl-container cd hodl && HODL_NAME="Chuck" && python3 tests/test_net.py
docker run -p 5000:5004 -v "$(pwd)":/home/hodl/ hodl-container cd hodl && HODL_NAME="Dave" && python3 tests/test_net.py