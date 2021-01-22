# Software to control the CROC
# Date: 22 Jan 2021
# Author: Giorgos PAPADOPOULOS

import spidev
import RPi.GPIO as GPIO
import time
import numpy as np

def create96bitWord():
	# from a config file get all the values for the CROC parameters
	# create a 96-bit word
	# and return it in -I think- decimal value


#==============================================
# Set the spi link
SCLKfreq = 1000000 # Frequency of the serial clokc (SCLK) in Hz
CNV = 0 # SYNC as written on DAC eval board is the equivalent of Chip Select (CS) or Slave Select (SS)
spi = spidev.SpiDev()
spi.open(0,CNV) # This is not actually necessary for CROC
# Set the mode. I want:
# SCLK to go from low to high -> POL=0
# MISO/MOSI get/set the bit at the rise of the SCLK pulse -> PHA=0, might work with PHA=1(?)
spi.mode = 0b01
spi.max_speed_hz = SCLKfreq


# SPI is only good for SCLK, MOSI and MISO
# We need 2 more signals: LOAD, READ
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
LOAD = 13 # pin number (randomly chosen)
READ = 15 # pin number (randomly chosen)
GPIO.setup(LOAD, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(READ, GPIO.OUT, initial=GPIO.LOW)

GPIO.output(LOAD, GPIO.LOW) # make sure it is low
GPIO.output(READ, GPIO.LOW) # make sure it is low


#==============================================
# Set the name of the config file that includes the CROC parameters
configfile = 'CROCparams.bcf'

#==============================================

# Send the 96-bit word to set the CROC register
wordparam = create96bitWord(configfile)
spi.writebytes(wordparam)
GPIO.output(LOAD, GPIO.HIGH)
GPIO.output(LOAD, GPIO.LOW) # make sure that there is not a proble to go HIGH and LOW so quickly



# Get the 96-bit word from the CROC register
GPIO.output(LOAD, GPIO.HIGH)
# >>> send a single SCLK pulse
GPIO.output(LOAD, GPIO.LOW)
out=spi.readbytes(12)









