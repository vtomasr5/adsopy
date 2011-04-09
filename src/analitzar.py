#!/usr/bin/env python
# coding: utf-8

import re
import fileinput

FITXER="/home/vjuan/uib/ADSO/adsopy/data/proves.log"

def obrir_fitxer(fitxer):
    ret = fileinput.input(fitxer)
    return ret

def punt1(fitxer):
    d = {}
    f = obrir_fitxer(fitxer)
    for i in f:
        res = re.split(" ", i)
        if res[9] != "-":
            d = res[9]
            print d
            #print res[9], res[6]

    f.close()

if __name__ == "__main__":
    punt1(FITXER)
