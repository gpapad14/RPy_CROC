#gnuplot
from pygnuplot import gnuplot
import numpy as np 
from termcolor import colored 

filename = 'scan3V3Rasp.txt'
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

g = gnuplot.Gnuplot(terminal = 'pngcairo font "arial,10" fontscale 1.0 size 600, 400',
                    output = '"gnuplotfig.png"')

g.plot('[-10:10] sin(x)',
       'atan(x)',
       'cos(atan(x))')