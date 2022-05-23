systemctl list-units --type=service
journalctl -u ledhandler3.service
systemctl restart ledhandler3.service
journalctl -u ledhandler4.service
systemctl restart ledhandler4.service