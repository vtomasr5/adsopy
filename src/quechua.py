#!/usr/bin/env python
# coding: utf-8

# AUTOR: Vicenç Juan Tomàs Montserrat
# LLICENCIA: GPL-3
# VERSIO: 0.1

##  @package quechua
#   Servidor web "estàtic" amb prefork escrit en python

import socket, os, sendfile, time
import mimetypes as mim
from stat import *
from multiprocessing import Process, Queue, current_process, Semaphore
import ConfigParser

FILE_CONFIG = "../data/quechua.conf"

##  Llegeix la configuració de la variable del fitxer de configuració
#   @param clau
def read_config(clau):
    cfg = ConfigParser.ConfigParser()
    try:
        cfg.read(FILE_CONFIG)
        valor = cfg.get('quechuad', clau)
        return valor
    except IOError, ex:
        print ("El fitxer no se pot llegir!")

##  Funció que contesta al socket
#   @param sock Socket
def respuesta(sock):
    try:
        OUT = sock.makefile()
        http_command = OUT.readline()
        headers = []
        command = http_command.split()
        #print "Commando:", command
        for line in OUT:
            if line.strip() == "": break
            headers.append(line)
        if command[0] == "GET":
            if command[1] == "/":
                filename = document_root + "/index.html"
            else:
                filename = document_root + command[1]
            try:
                FILE = open(filename, "rb")
                #print "Sending", filename
                m = mim.guess_type(filename)
                size = os.stat(filename)[ST_SIZE]
                mod = os.stat(filename)[ST_MTIME]
                t = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime(mod))
                OUT.write("HTTP/1.0 200 OK\r\n")
                OUT.write("Last-Modified: %s\r\n" % t)
                OUT.write("Content-Type: %s\r\n" % m[0])
                OUT.write("Content-Length: %d\r\n\r\n" % size)
                OUT.flush()
                sendfile.sendfile(OUT.fileno(), FILE.fileno(), 0, size)
            except IOError:
                OUT.write("HTTP 404 Fichero no existe\r\n")
                #print "Error con", filename
    except Exception, e:
            print "Error en la conexión", e
    OUT.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

host = read_config('host')
port = read_config('port')

s.bind((host, int(port)))
s.listen(1)

## Funció que inicia el servidor
def run_server(q,):
    i = 0
    p = current_process()
    while True:
        try:
            conn, addr = s.accept()
            #~ print "Actius:", sem_actius.get_value()
            # Incrementam el comptador de processos actius
            sem_actius.release()
            #print "Conexión desde:", addr, "PID:", os.getpid()
            # Contestam
            respuesta(conn)
            conn.close()
            # Decrementam el comptador de processos actius
            sem_actius.acquire()
            # Incrementam el numero de connexions del procés
            i += 1
            sem_lliures = sem_totals.get_value() - sem_actius.get_value()
            # Si el procés ha respost a 1000 connexions o hi ha més processos lliures que el màxim permés, el procés es mor
            if (i == 10) or (sem_lliures > max_processos_lliures):
                sem_totals.acquire()
                q.put(p.pid)
                break
        except socket.error:
            pass

dr = read_config('document_root')
env = os.getenv(dr)
lang = os.getenv('LANG')

# determinar el 'document_root' a l'escriptori
if env:
    if lang.startswith('es'):
        document_root = env.strip() + '/Escritorio'
    elif lang.startswith('en'):
        document_root = env.strip() + '/Desktop'
    elif lang.startswith('ca'):
        document_root = env.strip() + '/Escriptori'
    print 'Arrel: %s' % document_root
else:
    print "ERROR: Variable d'entorn %s no definida!" %env
    sys.exit(-1)

max_processos = int(read_config('max_processes'))
min_processos = int(read_config('min_processes'))
max_processos_lliures = int(read_config('max_spare_processes'))
min_processos_lliures = int(read_config('min_spare_processes'))

sem_totals = Semaphore(0)
sem_actius = Semaphore(0)

pids = set()
q = Queue()

# Cream el pool de procesos
for i in range(min_processos):
    sem_totals.release()
    p = Process(target=run_server, args=(q,))
    p.start()
    pids.add(p.pid)
    #print "Nou proces: ", p.pid

print "\nhttp://%s:%s\n" % (host, port)

while True:
    # controlam amb semàfors que el nombre de processos no surti dels límits establerts
    sem_lliures = sem_totals.get_value() - sem_actius.get_value()
    #~ print "Lliures:", sem_lliures
    while (sem_totals.get_value() < min_processos) or ((sem_totals.get_value() < max_processos) and (sem_lliures < min_processos_lliures)):
        #~ print "Totals:", sem_totals.get_value()
        sem_totals.release()
        p = Process(target=run_server, args=(q,)) # proces nou
        p.start()
        pids.add(p.pid)
        print "Nou proces:", p.pid

    pid = q.get(True) # espera
    pids.remove(pid)
    print "Ha acabat:", pid

