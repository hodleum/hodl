#!/usr/bin/env bash
echo "UNITTESTS:";echo;echo
python -m unittest
echo "FUNCTIONAL:";echo;echo
echo "TWNC:";echo
cd tests/testnet
./run_twnc.sh
cd tests/testnet
echo "COMPLETE TESTNET:";echo
./run_complete.sh
