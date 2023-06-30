# Nvidia Fan Control

Control the fan speed of NVida graphics cards based on a user-defined curve for Linux.

## Problem

There is no easy way to set up a temperature-fan speed curve on your own (like MSI Afterburner for Windows).
As a result, under heavy load, the video card quickly warms up to a temperature of 86C (186F) and above.
This is not the best mode for long device life.

## Solution

A script that will monitor the temperature of each GPU, check the curve profile and translate the fans
to the desired rotation speed.

like this:


![myplot.png](misc%2Fmyplot.png)

## Fast start

Edit the temp_profile.json in profiles

```JSON
{ "GPUS": [
  {"0": 5, "20":  15, "40":  35, "60":  75, "80": 95, "100":  100}
],
  "GPU_FAN_MAP": {"0": 1, "1": 0}
        }
```

"GPUS":

The key is the GPU temperature and value is the desired fan speed.

"GPU_FAN_MAP":

The key is the GPU number (id) and the value is the fan ID (this works for me, maybe yours will be different)

Create virtual environment:

`git clone `

`python3 -m venv venv`

`source venv/bin/activate`

Install libs:

`pip install -r requirements.txt`

Start the controller:

`python3 src/main.py`

### Run as .desktop application

Edit the path to the script in [FanController.desktop](FanController.desktop).
Copy to desktop and change file properties to allow execution.
