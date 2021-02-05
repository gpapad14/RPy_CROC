# Software to control the ASPIC
# Date: 5 Feb 2021
# Author: Giorgos PAPADOPOULOS
# Raspberry Pi 4: make sure to have installed the necessary packages before running the code.
# Git repo: https://github.com/gpapad14/RPy_CROC.git

import time
import numpy as np
import spidev

# Set the spi link
SCLKfreq = 1000000 # Frequency of the serial clokc (SCLK) in Hz
CNV = 0 # SYNC as written on DAC eval board is the equivalent of Chip Select (CS) or Slave Select (SS)
ASPICspi = spidev.SpiDev()
ASPICspi.open(0,CNV) # This is not actually necessary for CROC
# Set the mode. I want:
# SCLK to go from low to high -> POL=0
# MISO/MOSI get/set the bit at the rise of the SCLK pulse -> PHA=0, might work with PHA=1(?)
ASPICspi.mode = 0b01 # 0b.POL.PHA
ASPICspi.max_speed_hz = SCLKfreq


write = 128 # 0b10000000
read  = 0   # 0b00000000

def setASPIC(gain=1, rc=0, clamp=[1,1,1,1,1,1,1,1], AF1=0, TM=1): # random default values
    for reg in [0, 1, 2]: # There are 3 registers: 0, 1, 2
        message = []
        byte1 = write + reg
        message.append(byte1)
        message.append(0) # I want the 2nd byte (bits from 8 to 15) to be 0 -> 0b00000000
        if reg==0:
            byte3 = gain * 2**4 + rc # the gain is just moved to the write possition
        if reg==1:
            byte3 = 0b0 
            for i in range(8):
                byte3 += clamp[i] * 2**(8-1-i)
                #print(bin(byte3))
        if reg==2:
            byte3 = AF1*2 + TM
        message.append(byte3)
        print('Send:', bin(message[0]), bin(message[1]), bin(message[2]))
        ASPICspi.write(message) # send 3 bytes = 24 bits
        
def getASPIC()
    reaback=[]
    for reg in [0, 1, 2]: # There are 3 registers: 0, 1, 2
        message = []
        byte1 = read + reg
        message.append(byte1)
        ASPICspi.write(message) # send 1 byte = 8 bits
        readback.append(ASPICspi.readbytes(2)) # read 2 bytes = 16 bits
        print('Get register', reg, ':', bin(readback[1])) 


gain = 15 # gain of the 1st(?) amplifier from 1.4 to 6.6. Acceptable input values from 0 to 15
rc   = 0 # rc time constant from 250ns to 4μs. Acceptable input values from 0 to 15
clamp = [1, 0, 1, 1, 1, 0, 0, 1] # force the input of the channel to be sorted to a Vref. Acceptable input values 0 or 1
AF1 = 1 # Gain of the 1st(?) ampli equal to 1. Acceptable input values 0 or 1
TM  = 1 # Transparent Mode. Acceptable input values 0 or 1

# Every time we load the params for all 3 registers. It does not take long, but we will not load params often.
setASPIC(gain, rc, clamp, AF1, TM)
time.sleep(0.1)
# Every time we read the ASPIC, we read all 3 registers.
getASPIC()


