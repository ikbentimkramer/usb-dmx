## About

This is a hacked together python package to control a couple of dmx lights at a student association. Currently it can run a couple of pre-programmed lighting chases and change the speed at which the lights change.

This package works on python 3.9.6. 

## Installation

If you do not have python installed, download and install it from <https://www.python.org/>. [Git](https://git.scm.org/) is also required.

To install, run:
```
python -m pip install git+https://github.com/ikbentimkramer/usb-dmx.git
```

Now, to start the CLI, run
```
python -m usb_dmx <port>
```
with `<port>` being the serial port to connect to.