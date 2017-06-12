## Humidity
### Brief Introduction
This work is part of a larger project to build a low-cost environmental chamber for scientific research using a Raspberry Pi. This repository contains python code to read relative humidity and temperature from a DHT sensor (DHT11, DHT22, AM2302). In addition to reading data from a DHT sensor, code to turn on and off a bottlecap humidifier is included.

To make reading of the DHT sensor and control of the humidifier easy to change, a GUI is included.

### How to use this repository
**This code has only been tested in Python 2.7. Please send feedback if you attempt in Python 3.**

Before using this respository, make sure to clone the Adafruit DHT repository and follow instructions to install:
[Adafuit Python DHT](https://github.com/adafruit/Adafruit_Python_DHT)

After cloning this repository, it is possible to run the GUI by running `RHPanel.py`.

### To do...
* Circuit schematics
* Parts list
* Solenoid valve to control dry air
* Plot data
* Find alternative to Adafruit DHT code