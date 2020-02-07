## About
This is a hacked together python script to control a couple of dmx lights at my student association. Currently it can run a couple of pre-programmed lighting chases and change the speed at which the lights change.

The script works on python 3.8.1. 

## Installation
If you do not have python installed, download and install it from <https://www.python.org/>.

This package requires the packages `pyserial` and `dmx485`. To install using `pip` on the command line:

```
pip install --user pyserial
pip install --user dmx485
```

The dmx485 package on `pip` throws an error on windows. To fix this, open the dmx485 `__init__.py` in a text editor (on windows usually located at `%AppData%\Python\Python38\site-packages\dmx\__init__.py`) and find the line:

```
self.desc = self.ser.fileno()
```

And change it to:

```
# self.desc = self.ser.fileno()
```

Finally download this script and run it on the command line using:

```
python compudmx.py
```

## Usage

