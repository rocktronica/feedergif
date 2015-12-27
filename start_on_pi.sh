#!/bin/bash

ssh pi@pizero.local <<'ENDSSH'

kill $(ps aux | grep '[p]ython app.py' | awk '{print $2}')
cd ~/feedergif
screen -dm bash -c 'python app.py; exec sh'

ENDSSH
