# Software to control the EVAL-AD5791 20-bit DAC with a Raspberry Pi
# Date: 6 Nov 2020
# Author: Giorgos PAPADOPOULOS

#import spidev 
import time
from termcolor import colored 

SCLKfreq = 1000000 # Frequency of the serial clokc (SCLK) in Hz
SYNC = 0 # SYNC as written on DAC eval board is the equivalent of Chip Select (CS) or Slave Select (SS)
VrefP = 10. # Positive reference voltage of DAC in V
VrefN = -10. # Negative reference voltage of DACin V
DACresol = 20

# Do I need to specify the CS, MISO, MOSI and SCLK pins? Maybe not.
# Check it SYNC goes low when I send a word.
# Check if the 3 bytes are written in the sequence I think they are.
'''
spi = spidev.SpiDev()
spi.open(0,SYNC)
spi.mode = 0b10 # this is the option that was used by the Arduino, might be able to be different.
spi.max_speed_hz = SCLKfreq
'''

def startup():
	PU=[]
	PU.append(0b00100000)
	PU.append(0b00000000)
	PU.append(0b00010010)
	#spi.writebytes(PU)
	time.sleep(0.1)
	SetVoltageOutput(524288) # this value is supposed to be the Vout=0.0V
	return True

def SetVout(decIN):
	#SetVoltageOutput(decIN)
	SetVoltageOutput2(decIN)

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
				#spi.writebytes(WR)
				return WR


def SetVoltageOutput(decIN):
	if type(decIN)==type(int(1)):
		less8=False
		less16=False
		if decIN>=0 and decIN<2**20: # check if the input code is valid
			binIN=bin(decIN) # at this point the binIN is string
			#print(binIN,len(binIN)-2)
			if len(binIN)-2>0 and len(binIN)-2<=20: # additional unnecessary safety level
				
				write1byte = '0b0001'

				if len(binIN)-2>=8:
					write3byte = '0b'+str(binIN[-8:])
				else:
					write1byte += '0000'
					write2byte = '0b00000000'
					write3byte = '0b'
					for i in range(8-(len(binIN)-2)):
						write3byte += '0'
					write3byte += binIN[-(len(binIN)-2):]
					less8=True
					
				if len(binIN)-2>=16:
					write2byte = '0b'+str(binIN[-16:-8])
				elif not(less8):
					write1byte += '0000'
					write2byte ='0b'
					for i in range(16-(len(binIN)-2)):
						write2byte += '0'
					write2byte += binIN[-(len(binIN)-2):-8]
					less16=True

				if not(less16) and not(less8) : # if True it means that write3byte and w2b are written and w1b remains to be set 
					for i in range(20-(len(binIN)-2)):
						write1byte += '0'
					write1byte += binIN[-(len(binIN)-2):-16]

				#print(write1byte,write2byte,write3byte) # at this point the bytes are string-type
				write1byteINT=int(write1byte[2:], 2)
				write2byteINT=int(write2byte[2:], 2)
				write3byteINT=int(write3byte[2:], 2)
				WR=[]
				WR.append(write1byteINT)
				WR.append(write2byteINT)
				WR.append(write3byteINT)
				#print(WR) # Now the WR is a list of 3 numbers and can be sent to the DAC
				#spi.writebytes(WR)
				return WR

		else:
			print(colored('ERROR #1: Not an accepted integer input value','red'))
	elif type(decIN)==type('string') and (decIN[-1]=='v' or decIN[-1]=='V'):
		voltVal=float(decIN[:-1])
		if voltVal>=-10. or voltVal<=10.:
			print('Continue... (it is not written yet')

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
		#	print('ERROR ---')
		
def DACregout():
	PU=[]
	PU.append(0b10010000)
	PU.append(0b00000000)
	PU.append(0b00000000)
	#spi.xfer(PU)
	time.sleep(0.1)
	
	return True

SetVout(525000)
Scan()

