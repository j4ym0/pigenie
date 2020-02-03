#! /bin/bash

if [ ! -f src/energenie/drv/radio_rpi.so ]; then
    echo "Drivers not found!"
    chmod 755 src/energenie/drv/build_rpi
    cd src/energenie/drv/
    echo "Starting to build drivers"
    ./build_rpi
    cd ../..
fi
if [ ! -f src/energenie/drv/radio_rpi.so ]; then
  echo "Drivers found, starting monitor"
  python3 src/monitor.py
fi
