#!/bin/bash

apt update
apt install -y python3-venv python3-pip
python3 -m venv venv
./venv/bin/pip install -r app/requirements.txt

cat << 'EOF' > /etc/systemd/system/challwebjponix.service
[Unit]
Description=Chall Web JPO Nix Flask App
After=network.target

[Service]
WorkingDirectory=/root/challWebJPONix/app
ExecStart=/root/challWebJPONix/venv/bin/python /root/challWebJPONix/app/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable challwebjponix.service
systemctl start challwebjponix.service