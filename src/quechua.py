#!/usr/bin/env python
# coding: utf-8

# AUTOR: Vicenç Juan Tomàs Montserrat
# LLICENCIA: GPL-3
# VERSIO: 0.1

##  @package quechua
#   Servidor web "estàtic" amb prefork escrit en python

import socket
import os, sys, time
import sendfile
import ConfigParser
import logging

from stat import *
from multiprocessing import BoundedSemaphore

FILE_CONFIG = "../data/quechua.conf"

class Config():
    ##  Constructor de la clase Config
    #   @param file_config Fichero de configuración
    def __init__(self, file_config):
        self.file_config = file_config

    ##  Llegeix la configuració de la variable del fitxer de configuració
    #   @param clau
    def read_config(clau):
        cfg = ConfigParser.ConfigParser()
        try:
            cfg.read(self.file_config)
            valor = cfg.get('quechuad', clau)
            return valor
        except IOError, ex:
            print ("El fitxer no se pot llegir!")

class Server():
    ##  Constructor de la clase Server
    #   @param maxServers Numero máximo de procesos en el servidor
    #   @param minServers Numero mínimo de procesos en el servidor
    #   @param minSpareServers Numero mínimo de procesos en espera en el servidor
    #   @param maxSpareServers Numero máximo de procesos en espera en el servidor
    #   @param host Dirección IP
    #   @param port Puerto por donde escucha el servidor
    def __init__(self, maxServers, minServers, minSpareServers, maxSpareServers, host, port):
        self.maxServers = int(maxServers)
        self.minServers = int(minServers)
        self.minSpares = int(minSpareServers)
        self.maxSpares = int(maxSpareServers)
        self.host = host
        selg.port = int(port)

    def newProcess(self):
        return

    ##  Funció que contesta al socket
    #   @param sock Socket
    def respuesta(sock):
        try:
            OUT = sock.makefile()
            http_command = OUT.readline()
            headers = []
            command = http_command.split()
            print "Comanda:", command
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
                    print "Sending", filename
                    size = os.stat(filename)[ST_SIZE]
                    OUT.write("HTTP/1.0 200 Quechua\r\n")
                    OUT.write("Content-Length: %d\r\n\r\n" % size)
                    OUT.flush()
                    sendfile.sendfile(OUT.fileno(), FILE.fileno(), 0, size)

                except IOError:
                    OUT.write("HTTP 404 Fichero no existe\r\n")
                    print "Error con", filename
        except Exception, e:
                print "Error en la conexión", e
        OUT.close()

    ##  Inicia el servidor
    def start():
        loginfo('Servidor arrancat')

        sem_total = BoundedSemaphore(n_procs)
        sem_actius = BoundedSemaphore(n_procs)

        pid = os.fork()
        if pid == 0: # hijo
            i = 0
            while True:
                try:
                    conn, addr = s.accept()
                    print "Conexió desde: ", addr, "PID: ", os.getpid()
                    sem_actius.acquire()

                    respuesta(conn)
                    conn.close()

                    sem_actius.release()
                    i += 1
                    if i == 1000: exit(0)
                except socket.error:
                    pass

        elif pid > 0: # padre
            print "padre"
            return pid
        else: # error
            print "ERROR: Proceso %d no creado" % pid
            return None

    ##  Atura el servidor correctament
    def stop():
        try:
            while True:
                try:
                    os.kill(os.getpid(), signal.SIGTERM)
                except OSError: # cutre
                    break
                time.sleep(0.2)

            print "Aturant...", os.getpid()
        except IOError:
            print "El servidor ja està aturat!"

    dr = read_config('document_root')
    env = os.getenv(dr)
    lang = os.getenv('LANG')

    # determinar el 'document_root' a l'escriptori
    if env:
        if lang.startswith('es'):
            document_root = env.strip() + '/Escritorio'
        elif lang.startswith('en'):
            document_root = env.strip() + '/Desktop'

        print 'Arrel: %s' % document_root
        loginfo('Arrel: %s' % document_root)
    else:
        print "ERROR: Variable d'entorn %s no definida!" %env
        sys.exit(-1)

##  Punt d'inici del programa
if __name__ == '__main__':
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        host = read_config('host')
        port = read_config('port')

        s.bind((host, int(port)))
        s.listen(1)
        print('Escoltant...')
    except KeyboardInterrupt:
        print "\nSortint... ara!\n"
        sys.exit(-1)
    finally:
        s.close()

    pids = set()
    n_procs = read_config('max_processes')

    serv = Server()

    # Inici
    while True:
        for i in range(int(n_procs)):
            pid = start()
            pids.add(pid)
            print "Nou proces: ", pid

        try:
            (pid, status, rusage) = os.wait3(0) # os.WNOHANG
            if pid > 0:
                pids.remove(pid)
        except OSError:
            pass
        except KeyboardInterrupt:
            print "\nSortint... ara!\n"
            sys.exit(-1)

        print "Ha acabat:", pid, "stat:", status
