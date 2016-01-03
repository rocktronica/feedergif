#!/bin/bash

sudo pkill python

cd ~/feedergif

app_args=$(echo ${@:1})

screen -S feedergif_app -dm bash -c "python app.py $app_args"
screen -S feedergif_server -dm bash -c "sudo python server.py"