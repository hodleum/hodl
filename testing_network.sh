#!/bin/bash
docker run -p 5000:5001 -v "$(pwd)":/home/hodl/:ro --env HODL_NAME="Alice" hodl-container python3 -m unittest tests.test_net
docker run -p 5000:5002 -v "$(pwd)":/home/hodl/:ro --env HODL_NAME="Bob" hodl-container python3 -m unittest tests.test_net
docker run -p 5000:5003 -v "$(pwd)":/home/hodl/:ro --env HODL_NAME="Chuck" hodl-container python3 -m unittest tests.test_net
docker run -p 5000:5004 -v "$(pwd)":/home/hodl/:ro --env HODL_NAME="Dave" hodl-container python3 -m unittest tests.test_net
