#!/bin/bash
yes|sudo \cp *.service /etc/systemd/system/
sudo systemctl daemon-reload

sudo systemctl enable ledhandler1.service
sudo systemctl enable ledhandler2.service
sudo systemctl enable ledhandler3.service
sudo systemctl enable ledhandler4.service

sudo systemctl start ledhandler1.service
sudo systemctl start ledhandler2.service
sudo systemctl start ledhandler3.service
sudo systemctl start ledhandler4.service