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
	print('ERROR: wordparam was not created.')

print('wordparam =', wordparam)

