#!/usr/bin/env python
# coding: utf-8

# AUTOR: Vicenç Juan Tomàs Montserrat
# LLICENCIA: GPL-3
# VERSIO: 0.1

##  @package analitzar
#   Mòdul que analitza el fitxers log que produeix el servidor web Apache

#---- IMPORTS ----#

import re
import fileinput
import sys
import os

#---- FUNCIONS ----#

##  Funció que calcula el tamany total de cada fitxer
def punt1():
    f = fileinput.input(fitxer)
    d = {}
    for l in f: # iteram sobre ses linies
        array = re.split(" ", l)
        if not d.has_key(array[6]):
            d[array[6]] = array[9]

    f.close()
    for i in d.keys():
        print "Fitxer:", i, "Tamany:", d[i], "bytes"

##  Funció que calcula el tràfic total per fitxer
def punt2():
    f = fileinput.input(fitxer)
    d = {}
    for l in f: # iteram sobre ses linies
        array = re.split(" ", l)
        if not d.has_key(array[6]) and array[9] != '-':
            d[array[6]] = int(array[9])
        elif d.has_key(array[6]) and array[9] != '-':
            d[array[6]] = int(array[9]) + int(d[array[6]])

    f.close()
    for i in d.keys():
        print "Fitxer:", i, "Tràfic:", d[i], "bytes"

##  Funció que calcula el tràfic total per IP
def punt3():
    f = fileinput.input(fitxer)
    d = {}
    for l in f: # iteram sobre ses linies
        array = re.split(" ", l)
        if not d.has_key(array[0]) and array[9] != '-':
            d[array[0]] = int(array[9])
        elif d.has_key(array[0]) and array[9] != '-':
            d[array[0]] = int(array[9]) + int(d[array[0]])

    f.close()
    for i in d.keys():
        print "IP:", i, "Tràfic:", d[i], "bytes"

##  Funció que calcula el dia amb més tràfic
def punt4():
    f = fileinput.input(fitxer)
    d = {}
    clau = 0
    val = 0
    for l in f: # iteram sobre ses linies
        array = re.split(" ", l)
        array2 = re.split(":", array[3])
        if not d.has_key(array2[0]) and array[9] != '-':
            d[array2[0]] = int(array[9])
        elif d.has_key(array2[0]) and array[9] != '-':
            d[array2[0]] = int(array[9]) + int(d[array2[0]])

    f.close()
    for i in d.keys():
        if val < d[i]:
            val = d[i]
            key = i

    c = re.sub(r'^\[', '', i)
    print "Dia:", c, "Tràfic:", d[i], "bytes"

##  Funció que calcula l'hora amb més tràfic
def punt5():
    f = fileinput.input(fitxer)
    d = {}
    clau = 0
    val = 0
    for l in f: # iteram sobre ses linies
        array = re.split(" ", l)
        array2 = re.split(":", array[3])
        if not d.has_key(array2[1]) and array[9] != '-':
            d[array2[1]] = int(array[9])
        elif d.has_key(array2[1]) and array[9] != '-':
            d[array2[1]] = int(array[9]) + int(d[array2[1]])

    f.close()
    for i in d.keys():
        if val < d[i]:
            val = d[i]
            key = i

    print "Hora:", i+'h', "Tràfic:", d[i], "bytes"

##  Funció que calcula el dia amb més visitants per IP's diferents
def punt6():
    f = fileinput.input(fitxer)
    d = {}
    dia = 0
    con = 0
    for l in f: # iteram sobre ses linies
        array = re.split(" ", l)
        array2 = re.split(":", array[3])
        dic = {}
        if not d.has_key(array2[0]):
            d[array2[0]] = {}
            d[array2[0]]["cont"] = 1
            d[array2[0]][array[0]] = 0
        else:
            dic = d[array2[0]]
            if not dic.has_key(array[0]):
                d[array2[0]][array[0]] = 0
                d[array2[0]]["cont"] = 1 + d[array2[0]]["cont"]

    f.close()
    for i in d.keys():
        if con < d[i]["cont"]:
            con = d[i]["cont"]
            dia = i

    c = re.sub(r'^\[', '', dia)
    print "Dia:", c, "Sol·licituts:", con

##  Funció que calcula el nombre de fitxers amb codi 404
def punt7():
    f = fileinput.input(fitxer)
    d = {}
    n = 0
    for l in f: # iteram sobre ses linies
        array = re.split(" ", l)
        if not d.has_key(array[6]) and array[8] == '404':
            d[array[6]] = array[8]
            n += 1

    f.close()
    print "Numero de fitxers 404:", n

##  Funció que mostra un menú per pantalla
#   @param f Fitxer de log passat per paràmetre
def menu():
    print "\n----- Menú d'administració interactiu -----\n"
    print "1) Tamany de cada fitxer"
    print "2) Tràfic total per cada fitxer"
    print "3) Tràfic total per a cada direcciṕ IP analitzada"
    print "4) El dia amb més tràfic (en bytes servits)"
    print "5) L'hora amb més tràfic (en bytes servits)"
    print "6) El dia amb més visitants (IP diferents)"
    print "7) Fitxers sol·licitats no existents (codi 404)"
    print "Q) Sortir\n"

    res = raw_input("Opció: ")

    if len(res) != 1:
        print "\nALERTA: Opció incorrecte!"
        sys.exit(-1)

    if "1" in res:
        punt1()
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

#---- INICI DEL PROGRAMA  ----#

if __name__ == '__main__':
#   Comprovacions de que existeix el fitxer i de que, efectivament, es un fitxer.
    if len(sys.argv) != 2:
        print "ERROR: Error de paràmetres!. Ús: ./analitzar.py fitxer_log"
        sys.exit(-1)

    if not os.path.exists(sys.argv[1]):
        print "ERROR: '%s' no existeix!" % sys.argv[1]
        sys.exit(-2)

    if not os.path.isfile(sys.argv[1]):
        print "ERROR: '%s' no es un fitxer!" % sys.argv[1]
        sys.exit(-3)

    fitxer = sys.argv[1]

    while True:
        try:
            menu()
        except KeyboardInterrupt:
            print "\nSortint... ara!"
            sys.exit(1)
