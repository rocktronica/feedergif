#!/bin/bash

ssh pi@pizero.local \ '
mkdir -p ~/feedergif
mkdir -p ~/feedergif/logs
mkdir -p ~/feedergif/images
mkdir -p ~/feedergif/output

sudo pip install pycrypto
sudo pip install ecdsa
sudo pip install pysftp
sudo pip install Flask'

rsync -avz --delete app.py server.py --progress pi@pizero.local:~/feedergif/
