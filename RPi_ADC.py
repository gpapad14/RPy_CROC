# Software to control the EVAL-AD5791 20-bit DAC
# Date: 6 Nov 2020
# Author: Giorgos PAPADOPOULOS

import spidev
import RPi.GPIO as GPIO
import time
import numpy as np


def Read18bitDecimal(outlist):
    if len(outlist)!=3:
        print('ERROR #1')
    
    lsbyte=''
    midbyte=''
    msbyte=''
    
    # lsbyte
    if outlist[2]<64:
        lsbyte='00'
    elif outlist[2]<128:
        lsbyte+='0'
    lsbyte+=str(bin(outlist[2]))[2:-6]
    #print(lsbyte)
    
    # midbyte
    decim=2
    while decim<=128:
        if outlist[1]<decim:
            midbyte+='0'
        decim=decim*2
    midbyte+=str(bin(outlist[1]))[2:]
    #print(midbyte)
    
    # msbyte
    decim=2
    while decim<=128:
        if outlist[0]<decim:
            msbyte+='0'
        decim=decim*2
    msbyte+=str(bin(outlist[0]))[2:]
    #print(msbyte)
    
    outword=msbyte+midbyte+lsbyte
    #print(msbyte+' '+midbyte+' '+lsbyte)
    #print(int(outword,2))
    vout=int(outword,2)*10/(2**18)-5
    #print('Vout:', float('{:.4f}'.format(vout)))
    return vout
        
    


SCLKfreq = 1000000 # Frequency of the serial clokc (SCLK) in Hz
CNV = 0 # SYNC as written on DAC eval board is the equivalent of Chip Select (CS) or Slave Select (SS)

spi = spidev.SpiDev()
spi.open(0,CNV)
spi.mode = 0b01
spi.max_speed_hz = SCLKfreq

datafile = open('datafile.txt','w')
#spi.writebytes([0b0110101])
Vouts=[]
#meanval2=0
Nsamples=20000
for i in range(Nsamples):
    #spi.xfer([0b0110101])
    #spi.writebytes([0b0110101])
    out=spi.readbytes(3)
    #print(bin(out[0]), bin(out[1]), bin(out[2]))
    outputval=Read18bitDecimal(out)
    datafile.write(str(outputval)+'\n')
    #meanval2+=outputval
    Vouts.append(outputval)

meanval=np.mean(Vouts[50:])
stdval=np.std(Vouts[50:])
print('---1: Samples',Nsamples,'mean =',meanval,'std =',stdval)
#meanval2=meanval2/Nsamples
#print('---2: Samples = ',Nsamples,'mean =',meanval2)

datafile.close()
spi.close()
