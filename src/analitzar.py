#!/usr/bin/env python
# coding: utf-8

# AUTOR: Vicenç Juan Tomàs Montserrat
# LLICENCIA: GPL-3
# VERSIO: 0.1

##	@package analitzar
#	Mòdul que analitza el fitxers log que produeix el servidor web Apache

##### IMPORTS #####

import re
import fileinput
import sys
import os

##### FUNCIONS #####

##  Funció que calcula el tamany de cada fitxer
#	@param fitxer Fitxer de log
def punt1(fitxer):
    """
    documentació
    """
    d = []
    fitxer = fileinput.input(fitxer)
    for linia in fitxer:
        d.append(linia)

    fitxer.close()

def punt2():
    pass

def punt3():
    pass

def punt4():
    pass

def punt5():
    pass

def punt6():
    pass

def punt7():
    pass

##  Funció que mostra un menú per pantalla
#	@param f Fitxer de log
def menu(f):
    print "\n   Menú d'administració interactiu\n"
    print "1) Tamany de cada fitxer"
    print "2) Tràfic total per cada fitxer"
    print "3) Tràfic total per a cada direcciṕ IP analitzada"
    print "4) El dia amb més tràfic (en bytes servits)"
    print "5) L'hora amb més tràfic (en bytes servits)"
    print "6) El dia amb més visitants (IP diferents)"
    print "7) Fitxers sol·licitats no existents (codi 404)"
    print "Q) Sortir\n"

    res = raw_input("Opció: ")

    if "1" in res:
        punt1(f)
    elif "2" in res:
        punt2()
    elif "3" in res:
        punt3()
    elif "4" in res:
        punt4()
    elif "5" in res:
        punt5()
    elif "6" in res:
        punt6()
    elif "7" in res:
        punt7()
    elif "q" or "Q" in res:
        sys.exit(0)
    else:
        print "\nALERTA: Opció incorrecte!"

##### INICI DEL PROGRAMA  #####

##  Punt d'inici del programa
# 	Comprovacions de que existeix el fitxer i de que, efectivament, es un fitxer.
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "ERROR: Error de paràmetres!. Ús: ./analitzar.py fitxer_log"
        sys.exit(-1)

    if not os.path.exists(sys.argv[1]):
        print "ERROR: '%s' no existeix!" % sys.argv[1]
        sys.exit(-2)

    if not os.path.isfile(sys.argv[1]):
        print "ERROR: '%s' no es un fitxer!" % sys.argv[1]
        sys.exit(-3)
    else:
        FITXER = sys.argv[1]

    while True:
        try:
            menu(FITXER)
        except KeyboardInterrupt, e:
            print "\nSortint ja!..."
            sys.exit(1)
