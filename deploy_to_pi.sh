#!/bin/bash

ssh pi@raspberrypi.internal \ '
mkdir -p ~/feedergif
mkdir -p ~/feedergif/images
mkdir -p ~/feedergif/output

sudo pip install pysftp'

rsync -avz --delete app.py settings.ini --progress pi@raspberrypi.internal:~/feedergif/
