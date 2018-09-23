#!/bin/bash
docker stop Alice Bob Chuck Dave
docker rm Alice Bob Chuck Dave
docker network rm hodlnet
./test_sync.sh
sleep 15
docker container logs Alice
docker container logs Bob
docker container logs Chuck
docker container logs Dave
