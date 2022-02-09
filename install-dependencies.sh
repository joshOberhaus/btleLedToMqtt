#!/bin/bash
sudo apt-get install python3-venv
python3 -m venv /home/pi/btleLedVenv
source ~/btleLedVenv/bin/activate
pip install paho-mqtt
pip install bluepy