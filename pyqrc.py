import numpy as np
import glob
import os
import sys

def file_reading(name):
        command = "grep 'SCF Done:' " + name + " | tail -n1 > tmp_.txt"
        os.system(command)
        ff = open('tmp_.txt').readlines()
        if not len(ff) == 0:
                tmp = ff[0].split()
                E0 = np.round(float(tmp[-5]),10)
        else:
                E0 = 0

        command = "grep 'Optimization completed.' " + name + " | tail -n1 > tmp_.txt"
        os.system(command)
        ff = open('tmp_.txt').readlines()
        if not len(ff) == 0:
                tmp = ff[0].split()
                Opt  = 'Y'
        else:
                Opt  = 'N'

        command = "grep 'Normal termination of Gaussian 16 at' " + name + " | tail -n1 > tmp_.txt"
        os.system(command)
        ff = open('tmp_.txt').readlines()
        if not len(ff) == 0:
                tmp = ff[0].split()
                Complete  = 'Y'
        else:
                Complete  = 'N'

        command = "grep 'imaginary frequencies (negative Signs)' " + name + " | tail -n 1 > tmp_.txt"
        os.system(command)
        ff = open('tmp_.txt').readlines()
        if not len(ff) == 0:
                tmp = ff[0].split()
                Nimag = int(tmp[1])
                #os.system("grep -n 'Frequencies --' " + name +  " | head -n 1")
                #imagfreq = np.round(float(tmp[4]),4)
                #imagfreq = float(tmp[4]) if not tmp[4].startswith("(negative") else -float(tmp[5])
        else:
                Nimag = 0
                #imagfreq = 0.0

        command = "grep 'Frequencies --' " + name + " | head -n 1 > tmp_.txt"
        os.system(command)
        ff = open('tmp_.txt').readlines()
        if not len(ff) == 0:
                line = ff[0].strip()
                freq = line.split()[2]
                imagfreq = float(freq)
        else:
                imagfreq = 0.0

        command = "grep 'Sum of electronic and thermal Free Energies=' " + name + " | tail -n 1 > tmp_.txt"
        os.system(command)
        ff = open('tmp_.txt').readlines()
        if not len(ff) == 0:
                tmp = ff[0].split()
                G298K = np.round(float(tmp[-1]),10)
        else:
                G298K = 0

        os.system('rm tmp_.txt')
        return E0, G298K, Opt, Complete, Nimag, imagfreq

strFormat = '%-30s%-20s%-20s%-10s%-10s%-10s%-10s'
print(strFormat %('name','E0','G298K','Opt','Complete','Nimag','imagfreq'))
print('------------------------------------------------------------------------------------------------------')
lists = glob.glob('*.out')
lists.sort()
for ll in lists:
        if os.path.isfile(ll):
                E0,G298K,Opt,Complete,Nimag,imagfreq = file_reading(ll)
                print(strFormat %(ll,str(E0),str(G298K),str(Opt),str(Complete),str(Nimag),str(imagfreq)))

for ll in lists:
        if os.path.isfile(ll):
            E0,G298K,Opt,Complete,Nimag,imagfreq = file_reading(ll)
            if Nimag != 0 and -30 < imagfreq < 0:
                sname = ll.split('.')[0]
                old_inp = open(sname +'.com').readlines()[:7]
                opted = open(sname + '.xyz').readlines()[2:]
                new_inp = old_inp + opted + ['\n']
                new_inp[3] = new_inp[3].replace('opt=(MaxCyc=999)', 'opt=(MaxCyc=999,tight) Int=UltraFine ')
                open(sname + '.com','w').writelines(new_inp)



for ll in lists:
        if os.path.isfile(ll):
            E0,G298K,Opt,Complete,Nimag,imagfreq = file_reading(ll)
            if Nimag != 0 and imagfreq < -50:
            #if Nimag != 0:
                iname = ll.split('.')[0]
                os.system('python -m pyqrc ' + ll + ' --nproc 40 --mem 32GB')
                old_inp = open(iname + '.com').readlines()[:5]
                new_coord = open(iname + '_QRC.com').readlines()[6:]
                new_inp = old_inp + new_coord
                open(iname + '.com','w').writelines(new_inp)
                os.system('rm ' + iname + '.chk ' + iname + '_QRC.com ')