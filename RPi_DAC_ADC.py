# Software to control the EVAL-AD5791 20-bit DAC with a Raspberry Pi
# Date: 6 Nov 2020
# Author: Giorgos PAPADOPOULOS

import spidev 
import time
import datetime
from termcolor import colored
import numpy as np
import RPi.GPIO as GPIO

SCLKfreq = 1000000 # Frequency of the serial clokc (SCLK) in Hz

DAC_SYNC = 1 # SYNC as written on DAC eval board is the equivalent of Chip Select (CS) or Slave Select (SS)
ADC_CNV  =0  # CNV as written on ADC is the equivalent of Chip Select (CS) or Slave Select (SS)

DACspi = spidev.SpiDev()
DACspi.open(0,DAC_SYNC)
DACspi.mode = 0b10 # this is the option that was used by the Arduino, might be able to be different.
DACspi.max_speed_hz = SCLKfreq
startupBool = False

ADCspi = spidev.SpiDev()
ADCspi.open(0,ADC_CNV)
ADCspi.mode = 0b01 # this is the option that was used by the Arduino, might be able to be different.
ADCspi.max_speed_hz = SCLKfreq


def Read18bitDecimal(outlist):
    if len(outlist)!=3:
        print('ERROR #1')
    
    lsbyte=''
    midbyte=''
    msbyte=''
    
    # >>> lsbyte : Least Significant byte
    if outlist[2]<64:
        lsbyte='00'
    elif outlist[2]<128:
        lsbyte+='0'
    lsbyte += str(bin(outlist[2]))[2:-6]
    #print(lsbyte)

    # >>> midbyte : Middle byte
    decim=2
    while decim<=128:
        if outlist[1]<decim:
            midbyte+='0'
        decim=decim*2
    midbyte+=str(bin(outlist[1]))[2:]
    #print(midbyte)

    # >>> msbyte : Most Significant byte
    decim=2
    while decim<=128:
        if outlist[0]<decim:
            msbyte+='0'
        decim=decim*2
    msbyte+=str(bin(outlist[0]))[2:]
    #print(msbyte)

    outword = msbyte + midbyte + lsbyte
    #print(msbyte + ' ' + midbyte + ' ' + lsbyte)
    #print(int(outword,2))
    vout = int(outword,2)*10/(2**18)-5
    #print('Vout:', float('{:.4f}'.format(vout)))
    return vout

#DACvalue=ADCspi.readbytes(3)
#DACoutVal=Read18bitDecimal(DACvalue)

def startup():
    PU=[]
    PU.append(0b00100000)
    PU.append(0b00000000)
    PU.append(0b00010010)
    DACspi.writebytes(PU)
    time.sleep(0.1)
    SetDACout(524288) # this value is supposed to be the Vout=0.0V
    return True

def SetDACout(decIN):
    SetVoltageOutput2(decIN)
    #print('Set DACout =',decIN*20/(2**20)-10)

def SetVoltageOutput2(decIN):
    if type(decIN)==type(int(1)):
        #print(decIN, type(decIN))
        less8=False
        less16=False
        if decIN>=0 and decIN<2**20: # check if the input code is valid
            binIN=bin(decIN) # at this point the binIN is string
            #print(binIN,len(binIN)-2)
            if len(binIN)-2>0 and len(binIN)-2<=20: # additional unnecessary safety level
                if len(binIN)-2>=8:
                    write3byte = int(binIN[-8:], 2)
                else:
                    less8=True
                    write1byte = int('00010000',2)
                    write2byte = 0
                    write3byte = int(binIN[2:], 2)

                if len(binIN)-2>=16:
                    write2byte = int(binIN[-16:-8],2)
                elif not(less8):
                    less16=True
                    write1byte = int('00010000',2)
                    if len(binIN)-2==8:
                        write2byte = 0
                    else:
                        write2byte = int(binIN[2:-8], 2)

                if not(less16) and not(less8): # if True it means that write3byte and w2b are written and w1b remains to be set 
                    write1byte = 16
                    if len(binIN)-2>16:
                        write1byte += int(binIN[2:-16], 2)

                WR=[]
                WR.append(write1byte)
                WR.append(write2byte)
                WR.append(write3byte)
                #print(WR) # Now the WR is a list of 3 numbers and can be sent to the DAC
                DACspi.writebytes(WR)
                return WR

def Scan(start=267386, stop=781190, step=512, delay=0.1):
    # start=267386~-5V, stop=781190~+5V, step=512~10mV
    if type(start)!=type(int(1)) or type(stop)!=type(int(1)) or type(step)!=type(int(1)):
        print('Scan was not performed. Please give only integer inputs.')
    elif start<0 or stop<0 or step<-2**20 or start>2**20 or stop>2**20 or step>2**20:
        print('Scan was not performed. Please give parameters in the acceptable range.')
    elif stop<start:
        print('Start value cannot be lower that stop.')
    else:
        Nvalues=(stop-start)//step +1
        print('Total output values:',Nvalues)
        inp=start
        #counter=0
        while inp<stop:
            SetVout(inp)
            inp+=step
            #time.sleep(delay)
            #counter+=1
            #print('DACin =',inp)
        #if Nvalues!=counter:
        #   print('ERROR ---')

def ScanNSample(start=267386, stop=781190, step=512, delay=0.1, Nsamples=100):
    # start=267386~-5V, stop=781190~+5V, step=512~10mV
    if type(start)!=type(int(1)) or type(stop)!=type(int(1)) or type(step)!=type(int(1)):
        print('Scan was not performed. Please give only integer inputs.')
    elif start<0 or stop<0 or step<-2**20 or start>2**20 or stop>2**20 or step>2**20:
        print('Scan was not performed. Please give parameters in the acceptable range.')
    elif stop<start:
        print('Start value cannot be lower that stop.')
    else:
        Vouts=[]
        Nvalues=(stop-start)//step +1
        print('Total output values:',Nvalues)
        inp=start
        stepcounter=0
        print(colored('Scan starts now ...','green'))
        inittime=datetime.datetime.now()
        while inp<stop:
            VoutLoop=[]
            print('>>> Loop #'+str(stepcounter), 'DACin =',inp, 'DACout =',inp*20/(2**20)-10)
            SetDACout(inp)
            time.sleep(0.0001)
            for i in range(Nsamples):
                ReadDACvalue=ADCspi.readbytes(3)
                DACoutVal=Read18bitDecimal(ReadDACvalue)
                VoutLoop.append(DACoutVal)
                Vouts.append(DACoutVal)
            print('   ADCout =', np.mean(VoutLoop[1:]), '+/-', np.std(VoutLoop[1:])) 
            inp+=step
            #time.sleep(delay)
            stepcounter+=1
            #print('DACin =',inp)
        endtime=datetime.datetime.now()
        print(colored('Scan is complete!','green'))
        #if Nvalues!=stepcounter:
        #   print('ERROR ---')
        datafile = open('scan3.txt','w')
        datafile.write(str(inittime)+'\n')
        datafile.write(str(endtime)+'\n')
        for i in range(len(Vouts)):
            datafile.write(str(Vouts[i])+'\n')
        datafile.close()







#startup()
'''
for j in range(5):
    DACvalue=ADCspi.readbytes(3)
    DACoutVal=Read18bitDecimal(DACvalue)
    #print('Vout =',DACoutVal)
time.sleep(1)
SetDACout(268000)
time.sleep(0.01)
for j in range(5):
    DACvalue=ADCspi.readbytes(3)
    DACoutVal=Read18bitDecimal(DACvalue)
    #print('Vout =',DACoutVal)
'''

#startup()
#ScanNSample(start=500000, stop=580000, step=128, Nsamples=10000)

'''
Vouts=[]
inittime=datetime.datetime.now()
for j in range(4):
    print('>>> Loop #'+str(j))
    VoutLoop=[]
    for k in range(10000):
        ReadDACvalue=ADCspi.readbytes(3)
        DACoutVal=Read18bitDecimal(ReadDACvalue)
        VoutLoop.append(DACoutVal)
        Vouts.append(DACoutVal)
    print('   ADCout =', np.mean(VoutLoop[1:]), '+/-', np.std(VoutLoop[1:])) 

endtime=datetime.datetime.now()
print('Datataking is complete.')
datafile = open('scan2V5ref.txt','w')
datafile.write(str(inittime)+'\n')
datafile.write(str(endtime)+'\n')
for i in range(len(Vouts)):
    datafile.write(str(Vouts[i])+'\n')
datafile.close()
'''


DACspi.close()
ADCspi.close()

