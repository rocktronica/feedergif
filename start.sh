#!/bin/bash

sudo pkill python

cd ~/feedergif

app_args=$(echo ${@:1})

screen -S feedergif -dm bash -c "sudo python app.py  --url http://0.0.0.0:8081/capture $app_args"
screen -S server -dm bash -c "sudo python server.py"
screen -S camcamcam -dm bash -c "sudo python ~/camcamcam/app.py --host 0.0.0.0 --port 8081 --width 400 --height 300 --rotate 270"
