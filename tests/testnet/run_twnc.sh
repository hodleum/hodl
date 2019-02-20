#!/bin/bash
docker stop Alice Bob Chuck Dave miner evil_miner
docker rm Alice Bob Chuck Dave miner evil_miner
./twnc.sh
sleep 9
echo "Alice:"
docker container logs Alice
echo "Bob:"
docker container logs Bob
echo "Chuck:"
docker container logs Chuck
echo "Dave:"
docker container logs Dave
echo "miner:"
docker container logs miner
echo "evil_miner:"
docker container logs evil_miner

