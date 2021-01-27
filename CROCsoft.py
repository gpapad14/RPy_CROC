# Software to control the CROC
# Date: 22 Jan 2021
# Author: Giorgos PAPADOPOULOS
# Raspberry Pi 4: make sure to set the pythemv38 environment and them use $ python3.
# Git repo: https://github.com/gpapad14/RPy_CROC.git

import spidev
import RPi.GPIO as GPIO
import time
import numpy as np

#def create96bitWord():
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
SCLK = 5 # GPIO5
MOSI = 6 # GPIO6
MISO = 13 # GPIO13
LOAD = 19 # GPIO19
READ = 26 # GPIO26

GPIO.setup(SCLK, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(MOSI, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(LOAD, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(READ, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(MISO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # up or down is the default value of MISO signal of CROC

GPIO.output(SCLK, GPIO.LOW) # make sure it is low
GPIO.output(MOSI, GPIO.LOW) # make sure it is low
#GPIO.output(MISO, GPIO.LOW) # make sure it is low
GPIO.output(LOAD, GPIO.LOW) # make sure it is low
GPIO.output(READ, GPIO.LOW) # make sure it is low


#==============================================
# Set the name of the config file that includes the CROC parameters
configfile = 'CROCparams.bcf'

#==============================================

# Send the 96-bit word to set the CROC register
#wordparam = create96bitWord(configfile)
ch3 = '0b0001011010001101'
ch2 = '0b0001010010001101'
ch1 = '0b0001011100111110'
ch0 = '0b0001010100001111'
mbz = '0b00000000'
pol = '0b10000000'
off = '0b01111000'
polib = '0b10000000'

wordparam = '0b' + ch3[2:] + ch2[2:] + ch1[2:] + ch0[2:] + mbz[2:] + pol[2:] + off[2:] + polib[2:]
write=True

if write:
    for i in range(96):
        if wordparam[2+i]=='1':
            GPIO.output(MOSI, GPIO.HIGH) 
        GPIO.output(SCLK, GPIO.HIGH)
        GPIO.output(MOSI, GPIO.LOW)
        GPIO.output(SCLK, GPIO.LOW) # make sure that there is not a proble to go HIGH and LOW so quickly
        
    GPIO.output(LOAD, GPIO.HIGH)
    GPIO.output(LOAD, GPIO.LOW)

read=True
readback=''
time.sleep(0.02)

if read:
    GPIO.output(READ, GPIO.HIGH)
    GPIO.output(SCLK, GPIO.HIGH)
    GPIO.output(READ, GPIO.LOW)
    GPIO.output(SCLK, GPIO.LOW)
    for i in range(96):
        
        if GPIO.input(MISO):
            readback+='1'
        else:
            readback+='0'
        GPIO.output(SCLK, GPIO.HIGH)
        GPIO.output(SCLK, GPIO.LOW)
    readback ='0b'+readback
    if readback==wordparam:
        print('Success!!!')
    else:
        position=''
        print('ERROR!')
        for i in range(len(wordparam)):
            if wordparam[i]==readback[i]:
                position+=' '
            else:
                position+='!'
        print(position)
        print(readback)
        print(wordparam)
        


'''
read=False
if False:
    # Get the 96-bit word from the CROC register
    GPIO.output(LOAD, GPIO.HIGH)
    # >>> send a single SCLK pulse
    GPIO.output(LOAD, GPIO.LOW)
    out=spi.readbytes(12)
'''








