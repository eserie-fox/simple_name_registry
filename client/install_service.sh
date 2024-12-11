#!/bin/bash

sudo systemctl stop fox-name-registry

sudo cp fox-name-registry.service /etc/systemd/system/fox-name-registry.service
sudo systemctl daemon-reload
sudo systemctl enable fox-name-registry
sudo systemctl start fox-name-registry

sudo systemctl status fox-name-registry
