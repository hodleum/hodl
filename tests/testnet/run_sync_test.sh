#!/bin/bash
cd ../hodl
docker stop Alice Bob Chuck Dave
docker rm Alice Bob Chuck Dave
docker network rm hodlnet
test_sync.sh
sleep 15
echo "Alice:"
docker container logs Alice
echo "Bob:"
docker container logs Bob
echo "Chuck:"
docker container logs Chuck
echo "Dave:"
docker container logs Dave
