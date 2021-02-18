# Software to control the ASPIC
# Date: 11 Feb 2021
# Author: P. Privitera (modified from original program by Giorgos PAPADOPOULOS)
# Raspberry Pi 4: make sure to have installed the necessary packages before running the code.
# Git repo: https://github.com/gpapad14/RPy_CROC.git
import sys
import time
import numpy as np
import spidev
import RPi.GPIO as GPIO
######### 
# input values from command line
arg1 = sys.argv[1]
########
# will use GPIO17 for NSS (this is because of a bug with CE0/1 in spidev)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
NSS = 17
GPIO.setup(NSS, GPIO.OUT, initial=GPIO.HIGH)
# Set the spi link
SCLKfreq = 100000 # Frequency of the serial clokc (SCLK) in Hz
CNV = 0 # SYNC as written on DAC eval board is the equivalent of Chip Select (CS) or Slave Select (SS)
ASPICspi = spidev.SpiDev()
ASPICspi.open(0,CNV) # RPI port 0, device CE0
# Set the mode. I want:
# SCLK to go from low to high -> POL=0
# MISO/MOSI get/set the bit at the rise of the SCLK pulse -> PHA=0, might work with PHA=1(?)
ASPICspi.mode = 0b01 # 0b.POL.PHA
ASPICspi.max_speed_hz = SCLKfreq

# Default values for ASPIC initialization (see Table below)
gain = '1111' # gain of the 1st amplifier
rc   = '0000' # rc time constant
clamp = '00000011' # activate/deactivate a channel (force the input of the channel to Vref). Acceptable input values 0 or 1
AF1 = '1' # Gain of the 1st ampli equal to 1. Acceptable input values 0 or 1
TM  = '1' # Transparent Mode. Acceptable input values 0 or 1

def loadASPIC(gain='1111', rc='1000', clamp='11111111', AF1='1', TM='1', register=-1): # default values
	print("********* LOADING ASPIC SETTINGS ********")
	if register == 0 or register == -1:
# put together the first 24 bit word as three bytes:
# write and register 00: Gain and RC
		byte1 = [0,0,0]
		byte1[0] = int('10000000',base=2)
		byte1[1] = int('00000000',base=2)
		byte1[2] = int(gain + rc,base=2)
		loadbyte1 = byte1.copy()
		GPIO.output(NSS, GPIO.LOW)
		ASPICspi.xfer2(byte1) # send 3 bytes = 24 bits
		GPIO.output(NSS, GPIO.HIGH)

	if register == 1 or register == -1:
# put together the second 24 bit word:
# write and register 01: clamp
		byte2 = [0,0,0]
		byte2[0] = int('10000001',base=2)
		byte2[1] = int('00000000',base=2)
		byte2[2] = int(clamp,base=2)
		loadbyte2 = byte2.copy()
		GPIO.output(NSS, GPIO.LOW)
		ASPICspi.xfer2(byte2) # send 3 bytes = 24 bits
		GPIO.output(NSS, GPIO.HIGH)

	if register == 2 or register == -1:
# put together the third 24 bit word:
# write and register 10:  Special modes
		byte3 = [0,0,0]
		byte3[0] = int('10000010',base=2)
		byte3[1] = int('00000000',base=2)
		byte3[2] = int('000000' + AF1 + TM,base=2)
		loadbyte3 = byte3.copy()
		GPIO.output(NSS, GPIO.LOW)
		ASPICspi.xfer2(byte3) # send 3 bytes = 24 bits
		GPIO.output(NSS, GPIO.HIGH)

# print uploaded words in binary
	print("******** LOADED ********* ")
	if register == 0 or register == -1:
		written1 = ','.join([format(x, '08b') for x in loadbyte1])
		print("Gain and RC register: ",written1)
	if register == 1 or register == -1:
		written2 = ','.join([format(x, '08b') for x in loadbyte2])
		print("Clamp register:       ",written2)
	if register == 2 or register == -1:
		written3 = ','.join([format(x, '08b') for x in loadbyte3])
		print("Special mode register:",written3)
	print("******** READ ********* ")
	if register == 0 or register == -1:
		read1 = ','.join([format(x, '08b') for x in byte1])
		print("Gain and RC register: ",read1)
	if register == 1 or register == -1:
		read2 = ','.join([format(x, '08b') for x in byte2])
		print("Clamp register:       ",read2)
	if register == 2 or register == -1:
		read3 = ','.join([format(x, '08b') for x in byte3])
		print("Special mode register:",read3)

def readASPIC():
    print("********* READING ASPIC SETTINGS ********")
# Read register 00: Gain and RC
    byte1 = [0,0,0]
    byte1[0] = int('00000000',base=2)
    GPIO.output(NSS, GPIO.LOW)
    ASPICspi.xfer2(byte1) # send three  byte
    GPIO.output(NSS, GPIO.HIGH)

# Read register 01: clamp
    byte2 = [0,0,0]
    byte2[0] = int('00000001',base=2)
    GPIO.output(NSS, GPIO.LOW)
    ASPICspi.xfer2(byte2) # send 1 byte
    GPIO.output(NSS, GPIO.HIGH)

# Read register 10: Special modes
    byte3 = [0,0,0]
    byte3[0] = int('00000010',base=2)
    GPIO.output(NSS, GPIO.LOW)
    ASPICspi.xfer2(byte3) # send 1 byte
    GPIO.output(NSS, GPIO.HIGH)

# print read words in binary
    message1 = ','.join([format(x, '08b') for x in byte1])
    print("Gain and RC register: ",message1)
    message2 = ','.join([format(x, '08b') for x in byte2])
    print("Clamp register:       ",message2)
    message3 = ','.join([format(x, '08b') for x in byte3])
    print("Special mode register:",message3)

########### HERE STARTS THE PROGRAM ##################################
options =  ['INIT','READ','REG0','REG1','REG2']
if arg1 not in options:
   print ("Please input:")
   print ("INIT    to initialize the ASPIC")
   print ("READ    to read the ASPIC")
   print ("REG0    to change Gain+RC register")
   print ("REG1    to change Clamp register")
   print ("REG2    to change Special modes register")
   sys.exit()

if arg1 == 'INIT':
	loadASPIC(gain, rc, clamp, AF1, TM, -1)

if arg1 == 'READ':
	readASPIC()

allowed =  ['0000','0001','0010','0011','0100','0101','0110','0111','1000','1001','1010','1011','1100','1101','1110','1111']
if arg1 == 'REG0':
	print ("GAIN ?  (as 4 bit binary word)")
	print("4 bit  gain")
	print("0000   1.59")
	print("0001   1.91")
	print("0010   2.24")
	print("0011   2.56")
	print("0100   2.90")
	print("0101   3.22")
	print("0110   3.54")
	print("0111   3.85")
	print("1000   4.32")
	print("1001   4.64")
	print("1010   4.96")
	print("1011   5.27")
	print("1100   5.60")
	print("1101   5.92")
	print("1110   6.23")
	print("1111   6.55")
	gain = input("please type the 4-bit gain:  ")
	if gain not in allowed:
		print ("This value is not allowed!",gain)
		sys.exit()
	print ("Selected gain",gain)

	print ("RC ?  (as 4 bit binary word)")
	print("4 bit   RC (ns)")
	print("1111    252")
	print("0111    301")
	print("1011    323")
	print("0011    348")
	print("1101    376")
	print("0101    410")
	print("1001    450")
	print("0001    500")
	print("1110    561")
	print("0110    640")
	print("1010    744")
	print("0010    888")
	print("1100   1103")
	print("0100   1453")
	print("1000   2132")
	print("0000   4000")
	rc = input("please type the 4-bit RC:  ")
	if rc not in allowed:
		print ("This value is not allowed!",rc)
		sys.exit()
	print ("Selected rc",rc)
	loadASPIC(gain, rc, clamp, AF1, TM, 0)

if arg1 == 'REG1':
	print ("CLAMP ?   8 bit binary word")
	clamp = input("please type the 8-bit Clamp word:  ")
	try:
		testbin = int(clamp,base=2)
	except ValueError:
		print("This value is not allowed! ",clamp)
		sys.exit()
	print ("Selected Clamp ",clamp)
	loadASPIC(gain, rc, clamp, AF1, TM, 1)

if arg1 == 'REG2':
	allowed = ['0','1']
	print ("Special modes (0 or 1)")
	AF1 = input("please type AF1:  ")
	if AF1 not in allowed:
		print ("This value is not allowed!",AF1)
		sys.exit()
	TM = input("please type TM:  ")
	if TM not in allowed:
		print ("This value is not allowed!",TM)
		sys.exit()
	print ("Selected AF1 TM ",AF1,TM)
	loadASPIC(gain, rc, clamp, AF1, TM, 2)

ASPICspi.close()