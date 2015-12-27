# feedergif

WiP to send me GIFs of my cat eating food when I'm not around

![Hey bud](http://rocktronica.github.io/feedergif/1450364853.gif)

## Tech

- Old iPhone w/ [iPCamera](https://itunes.apple.com/us/app/ipcamera-high-end-network/id570912928?mt=8) app
- Python script on Raspberry Pi connected to same home network
- Server for hosting images
- [Hue](http://www2.meethue.com/en-us/products/) lights
- Misc IFTTT triggers for convenience


### Bugs

- gif halts on empty or corrupt photos
- pi can run out of space causing curl error 23
- if light switch is off, lights won't turn on
- starting script immediately into active timer should delete preexisting photos

### Needs
