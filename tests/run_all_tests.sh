echo "UNITTESTS:\n\n"
python -m unittest
echo "FUNCTIONAL:\n\n"
echo "TWNC:\n"
./testnet/run_twnc.sh
echo "COMPLETE TESTNET:\n"
./testnet/run_complete.sh
