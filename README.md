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

```python
curve_nodes = {
    0: 5,
    20: 15,
    40: 35,
    60: 75,
    80: 95,
    100: 100,
}
```

Where key is the GPU temperature and value is the desired fan speed.