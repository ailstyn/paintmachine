from os import fork
from pathlib import Path
from signal import signal, SIGTERM
from subprocess import run
from time import monotonic, sleep

import 
import board
import busio
from gpiozero import Device, Button
from gpiozero.pins.pigpio import PiGPIOFactory
from PIL import Image, ImageDraw, ImageFont
import pigpio

from hx711 import CH_A_GAIN_64, CH_A_GAIN_128, HX711
from papamaclib.argsandlogs import AL
from papamaclib.colortext import getLogger
