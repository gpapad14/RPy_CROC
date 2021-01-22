# Software to control the EVAL-AD5791 20-bit DAC with a Raspberry
# Date: 6 Nov 2020
# Author: Giorgos PAPADOPOULOS

import spidev 
import time
from termcolor import colored 

SCLKfreq = 1000000 # Frequency of the serial clokc (SCLK) in Hz
CNV = 0 # it is the equivalent of Chip Select (CS) or Slave Select (SS)
ADCbits = 18

# Do I need to specify the CS, MISO, MOSI and SCLK pins? Maybe not.
# Check it SYNC goes low when I send a word.
# Check if the 3 bytes are written in the sequence I think they are.

spi = spidev.SpiDev()
spi.open(0,CNV)
spi.mode = 0b01 
spi.max_speed_hz = SCLKfreq


def startup():
	PU=[]
	PU.append(0b00100000)
	PU.append(0b00000000)
	PU.append(0b00010010)
	spi.writebytes(PU)
	time.sleep(0.1)
	SetVoltageOutput(524288) # this value is supposed to be the Vout=0.0V
	return True
