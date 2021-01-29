# Software to control the CROC
# Date: 27 Jan 2021
# Author: Giorgos PAPADOPOULOS
# Raspberry Pi 4: make sure to set the pythemv38 environment and them use $ python3.
# This is the final version (v3), full and complete!
# After loading the params you can unplug the Raspberry Pi.
# Git repo: https://github.com/gpapad14/RPy_CROC.git

import RPi.GPIO as GPIO
import time
import numpy as np
import datetime
import sys

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
GPIO.output(LOAD, GPIO.LOW) # make sure it is low
GPIO.output(READ, GPIO.LOW) # make sure it is low

#============================================================================================

def create_wordparam(gain=[0,0,0,0], cf1=[0,0,0,0], nen=[0,0,0,0], rc=[0,0,0,0], tran=[1,1,1,1], ven=[1,1,1,1], pol=0, off=0, polib=0):
    wordparam='0b'
    for ichan in range(4):
        gainSTR = str(bin(gain[ichan]))
        for i in range(6-len(gainSTR[2:])):
            wordparam+='0' 
        wordparam+=gainSTR[-1:1:-1]
        wordparam+=str(cf1[ichan])
        wordparam+=str(nen[ichan])
        rcSTR = str(bin(rc[ichan]))
        for i in range(6-len(rcSTR[2:])):
            wordparam+='0' 
        wordparam+=rcSTR[-1:1:-1]
        wordparam+=str(tran[ichan])
        wordparam+=str(ven[ichan])

    wordparam+='00000000' # MBZ: Must Be Zero, DO NOT CHANGE THIS!

    polSTR = str(bin(pol))
    for i in range(8-len(polSTR[2:])):
        wordparam+='0' 
    wordparam+=polSTR[-1:1:-1] 

    offSTR = str(bin(off))
    for i in range(8-len(offSTR[2:])):
        wordparam+='0' 
    wordparam+=offSTR[-1:1:-1]

    polibSTR = str(bin(polib))
    for i in range(8-len(polibSTR[2:])):
        wordparam+='0' 
    wordparam+=polibSTR[-1:1:-1]

    #print('wordparam =', wordparam, len(wordparam[2:]))
    if len(wordparam[2:])!=96:
        return False
    return wordparam


def programCROC(wordparam):
    print('>>> Programming CROC')
    if type(wordparam)==type(1):
        wordparamBIN=bin(wordparam)
        wordparam='0b'
        
        for i in range (96-len(wordparamBIN[2:])):
            wordparam+='0'
        wordparam+=wordparamBIN[2:]
    elif type(wordparam)==type('string') and not(wordparam[:2]=='0b'):
        wordparamINT=int(wordparam)
        wordparamBIN=bin(wordparamINT)
        wordparam='0b'
        for i in range (96-len(wordparamBIN[2:])):
            wordparam+='0'
        wordparam+=wordparamBIN[2:]
    #print(wordparam)
    
    for i in range(96):
        if wordparam[2+i]=='1':
            GPIO.output(MOSI, GPIO.HIGH) 
        GPIO.output(SCLK, GPIO.HIGH)
        GPIO.output(MOSI, GPIO.LOW)
        GPIO.output(SCLK, GPIO.LOW)
    GPIO.output(LOAD, GPIO.HIGH)
    GPIO.output(LOAD, GPIO.LOW)
    
    time.sleep(0.02)
    return wordparam
 

def readbackCROC():
    print('>>> Readback CROC register.')
    readback=''
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
    time.sleep(0.05)

    return readback


def checkLoadRead(readParams, loadParams):
    print('>>> Comparing loaded 96-bit word with readback.')
    if readParams==loadParams:
        return True
    else:
        position=''
        print('ERROR!')
        for i in range(len(loadParams)):
            if loadParams[i]==readParams[i]:
                position+=' '
            else:
                position+='!'
        print(position)
        print(loadParams)
        print(readParams)
        return False


#============================================================================================

test=False
if test:
    print('>>> Started long test.')
    secatt=0 # second attempt to load the parameters if the first time they readback wrong
    unfixed=0
    ntotal=0
    timei = datetime.datetime.now().time()
    print(timei)
    for wordparams in range(0, 2**96, 2**84+3000000):
        ntotal+=1
        loadParams = programCROC(wordparam)
        #print(loadParams)
        readParams = readbackCROC()
        if loadParams!= readParams:
            #print('Second attempt')
            secatt+=1
            time.sleep(0.1)
            #loadParams = programCROC(wordparam) # if the readback was not done correctly, there is no need to load again the params
            #print(loadParams)
            readParams = readbackCROC()
        if not(checkLoadRead(readParams, loadParams)):
            unfixed+=1
        #time.sleep(1)
    
    timef=datetime.datetime.now().time()
    print(timef)
    print('Total tests:', ntotal, 'second attempts:', secatt, 'unfixed:', unfixed)
# 4% to readback the register wrong, 96% for a second readback to return the correct register 

gain = [5, 5, 5, 5]
cf1  = [0, 0, 0, 0]
nen  = [1, 1, 1, 1]
rc   = [0, 0, 0, 0]
tran = [1, 1, 1, 1]
ven  = [1, 1, 1, 1]
pol  = 128
off  = 120
polib= 128
wordparam = create_wordparam(gain, cf1, nen, rc, tran, ven, pol, off, polib)
if not(wordparam):
    sys.exit('ERROR: wordparam was not created.')
print('wordparam =', wordparam)

loadParams = programCROC(wordparam)
#print(loadParams)
readParams = readbackCROC()
# print(type(readParams))
checkLoadRead(readParams, loadParams)




