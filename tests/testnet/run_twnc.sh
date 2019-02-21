#!/bin/bash
docker stop Alice Bob Chuck Dave miner0 miner1 miner2  evil_miner
docker rm Alice Bob Chuck Dave miner0 miner1 miner2 evil_miner
./twnc.sh
sleep 20
echo "Alice:"
docker container logs Alice
echo "Bob:"
docker container logs Bob
echo "Chuck:"
docker container logs Chuck
echo "Dave:"
docker container logs Dave
echo "miner0:"
docker container logs miner0
echo "miner1:"
docker container logs miner1
echo "miner2:"
docker container logs miner2
echo "evil_miner:"
docker container logs evil_miner

