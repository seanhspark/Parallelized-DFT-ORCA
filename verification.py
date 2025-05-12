import numpy as np
import glob
import os
import sys

def file_reading(name):
    command = "grep 'SCF Done:' " + name + " 2> /dev/null | tail -n1 > tmp_.txt"
    os.system(command)
    ff = open('tmp_.txt').readlines()
    if not len(ff) == 0:
        tmp = ff[0].split()
        E0 = np.round(float(tmp[-5]), 10)
    else:
        E0 = 0.000

    command = "grep 'Optimization completed.' " + name + " 2> /dev/null | tail -n1 > tmp_.txt"
    os.system(command)
    ff = open('tmp_.txt').readlines()
    if not len(ff) == 0:
        tmp = ff[0].split()
        Opt = 'Y'
    else:
        Opt = 'N'

    command = "grep 'Normal termination of Gaussian 16 at' " + name + " 2> /dev/null | tail -n1 > tmp_.txt"
    os.system(command)
    ff = open('tmp_.txt').readlines()
    if not len(ff) == 0:
        tmp = ff[0].split()
        Complete = 'Y'
    else:
        Complete = 'N'
    command = "grep 'imaginary frequencies (negative Signs)' " + name + " 2> /dev/null | tail -n 1 > tmp_.txt"
    os.system(command)
    ff = open('tmp_.txt').readlines()
    if not len(ff) == 0:
        tmp = ff[0].split()
        Nimag = int(tmp[1])
    else:
        Nimag = 0

    command = "grep 'Frequencies --' " + name + " 2> /dev/null | head -n 1 > tmp_.txt"
    os.system(command)
    ff = open('tmp_.txt').readlines()
    if not len(ff) == 0:
        line = ff[0].strip()
        freq = line.split()[2]
        imagfreq = float(freq)
    else:
        imagfreq = 0.0

    command = "grep 'Sum of electronic and thermal Free Energies=' " + name + " 2> /dev/null | tail -n 1 > tmp_.txt"
    os.system(command)
    ff = open('tmp_.txt').readlines()
    if not len(ff) == 0:
        tmp = ff[0].split()
        G298K = np.round(float(tmp[-1]), 10)
    else:
        G298K = 0

    os.system('rm tmp_.txt')
    return E0, G298K, Opt, Complete, Nimag, imagfreq
strFormat = '%-30s%-20s%-20s%-10s%-10s%-10s%-10s'

# Open the log file
with open('geo_opt_result.log', 'w') as log_file:
    # Write headers to the log file
    log_file.write(strFormat % ('name', 'E0', 'G298K', 'Opt', 'Complete', 'Nimag', '1st_freq') + '\n')
    log_file.write('-------------------------------------------------------------------------------------------------------\n')
    
    # Process each .out file
    lists = glob.glob('*.out')
    lists.sort()
    for ll in lists:
        if os.path.isfile(ll):
            E0, G298K, Opt, Complete, Nimag, imagfreq = file_reading(ll)
            # Write the output for each file to the log file
            log_file.write(strFormat % (ll, str(E0), str(G298K), str(Opt), str(Complete), str(Nimag), str(imagfreq)) + '\n')
