# feedergif

WiP to send me GIFs of my cat eating food when I'm not around

![Hey bud](example.gif)

## To run

``` bash
ssh -T name@pi.local "bash -s" -- < start.sh [arguments to pass to app.py]
```

## Tech

- Webcamera,  [iPCamera](https://itunes.apple.com/us/app/ipcamera-high-end-network/id570912928?mt=8), or Facetime/rPi camera via [camcamcam](https://github.com/rocktronica/camcamcam)
- Python script on Raspberry Pi connected to same home network
- Server for hosting images
- [Hue](http://www2.meethue.com/en-us/products/) lights
- Misc IFTTT triggers for convenience

### Bugs

- failed gifs still upload when they shouldn't
- pi can run out of space causing curl error 23
- if light switch is off, lights won't turn on
- starting script immediately into active timer should delete preexisting photos
- curl errors should not be silent
- run scripts in loops?
- decouple ifttt lights vs email -- missing images shouldn't get email

### Needs

- log misc calls
- don't require stftp or ifttt
- errors from bad arguments don't show in logs
- IOError: [Errno 13] Permission denied: '/home/tommy/feedergif/logs/debug.log'
