#!/bin/bash
docker stop Alice Bob Chuck Dave miner0 miner1 miner2  evil_miner
docker rm Alice Bob Chuck Dave miner0 miner1 miner2 evil_miner
rm -f ../db/pok-2283324386201704913611015020843666292235918222617817014529141752335014299241241 ../db/pok-17996223138107222202377230874529513975511642551523777249172252515418524872198194 ../db/pok-109672917314017523867209239114132102118240421885719212451951543047141123164179232135140
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

