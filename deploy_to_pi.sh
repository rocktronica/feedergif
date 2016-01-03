#!/bin/bash

ssh tommy@feedergif.local \ '
mkdir -p ~/feedergif
mkdir -p ~/feedergif/logs
mkdir -p ~/feedergif/images
mkdir -p ~/feedergif/output

sudo pip install pycrypto ecdsa pysftp Flask
'

rsync -avz --delete app.py server.py start.sh templates --progress tommy@feedergif.local:~/feedergif/
