# NVidia Fan Control

Сontrol the fan speed of NVidia graphics cards based on a user-defined curve for Linux.

## Problem

There is no easy way to set up a temperature-fan speed curve on your own (as in MSI Aftrerburner for Windows).
As a result, under heavy load, the video card quickly warms up to a temperature of 86C (186F) and above.
This is not the best mode for long device life.

## Solution

A script that will monitor the temperature of each GPU, check the curve profile and translate the fans
to the desired rotation speed.
