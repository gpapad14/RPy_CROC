# Software to control the EVAL-AD5791 20-bit DAC
# Date: 6 Nov 2020
# Author: Giorgos PAPADOPOULOS

import spidev 
import time

SCLKfreq = 1000000 # Frequency of the serial clokc (SCLK) in Hz
SYNC = 0 # SYNC as written on DAC eval board is the equivalent of Chip Select (CS) or Slave Select (SS)
VrefP = 10. # Positive reference voltage of DAC in V
VrefN = -10. # Negative reference voltage of DACin V
DACresol = 20

# Do I need to specify the CS, MISO, MOSI and SCLK pins? Maybe not.
# Check it SYNC goes low when I send a word.
# Check if the 3 bytes are written in the sequence I think they are.

spi = spidev.SpiDev()
spi.open(0,SYNC)
spi.mode = 0b10
spi.max_speed_hz = SCLKfreq


PU1byte = 0b00100000
PU2byte = 0b00000000
PU3byte = 0b00010010
PU=[]
PU.append(PU1byte)
PU.append(PU2byte)
PU.append(PU3byte)
#spi.xfer(PU)
spi.writebytes(PU)

#time.sleep(0.5)
'''
Write1byte = 0b00011000
Write2byte = 0b00000000
Write3byte = 0b00000000
spi.xfer(Write1byte,Write2byte,Write3byte)
'''


