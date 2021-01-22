
import numpy as np 
from termcolor import colored 
import matplotlib.pyplot as plt


filename = 'scan1.txt'
file = open(filename, 'r')
lines = file.readlines()
inittime=lines[0]
endtime=lines[1]

print('# of lines',len(lines))
ADCout=[]
ADCoutstepsMean=[]
ADCoutstepsStd=[]

i=2
data=len(lines)
while i<data:
	ADCout.append(float(lines[i]))
	i+=1
xaxis=range(data-2)

plt.plot(xaxis, ADCout, marker='.', linestyle='')
plt.grid(True)
plt.title(filename)
plt.xlabel('sample')
plt.ylabel('ADC output (V)')
plt.tight_layout()
plt.savefig(filename[:-4]+'.png')
plt.show()
