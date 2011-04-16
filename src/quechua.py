#!/usr/bin/env python
# coding: utf-8

# AUTOR: Vicenç Juan Tomàs Montserrat
# LLICENCIA: GPL-3
# VERSIO: 0.1

import socket
import os, sys, time
import sendfile
import ConfigParser
import logging

from stat import *

FILE_CONFIG = "../data/quechua.conf"

def read_config(clau):
    cfg = ConfigParser.ConfigParser()
    try:
        cfg.read([FILE_CONFIG])
        valor = cfg.get('quechuad', clau)
        return valor
    except IOError, ex:
        print "ERROR: El fitxer no se pot llegir!\n"
        print ex

def set_config(clau, valor):
    cfg.set('quechuad', clau, valor)

def write_config():
    try:
        f = open(FILE_CONFIG, 'w')
        config_parser.write(cfg)
        f.close()
    except IOError, ex:
        print "ERROR: El fitxer no se pot modificar!\n"
        print ex

    debug("Configuració guardada")

def debug(message):
    print "%s - %s" % (time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), message)

def log(level, message):
    """ escriu un missatge de log al fitxer de logs """
    logger.log(level, message)

def respuesta(sock):
    try:
        OUT = sock.makefile()
        http_command = OUT.readline()
        headers = []
        command = http_command.split()
        print "Commando:", command
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
                OUT.write("HTTP/1.0 200 Va be\r\n")
                OUT.write("Content-Length: %d\r\n\r\n" % size)
                OUT.flush()
                sendfile.sendfile(OUT.fileno(), FILE.fileno(), 0, size)

            except IOError:
                OUT.write("HTTP 404 Fichero no existe\r\n")
                print "Error con", filename
    except Exception, e:
            print "Error en la conexión", e
    OUT.close()

def start():
    logging.debug("prova debug")
    try:
        f = read_config('pid_file')
        fpid = open(f, 'r')
        fpid = int(fpid.read())
        print "El servidor ja està en marxa!, PID %s" % fpid.read()
        return
    except IOError:
        print "Arrancant..."

    debug("Servidor en marxa")
    # afegir codi a partir d'aqui

def stop():
    try:
        f = read_config('pid_file')
        fpid = open(f, 'r')
        fpid = int(fpid.read())
        while True:
            try:
                os.kill(fpid, signal.SIGTERM)
            except OSError: # cutre
                break
            time.sleep(0.2)

        print "Aturant..."
    except IOError:
        print "El servidor ja està aturat!"

def restart():
    stop()
    time.sleep(1)
    start()

def init_logger():
    logger = logging.getLogger('quechua')
    log = read_config('log_file')
    hdlr = logging.FileHandler(log)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        init_logger()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        s.bind(("", 10000))
        s.listen(1)

        pids = set()

        try:
            {'start': start,
             'stop': stop,
             'restart': restart}[sys.argv[1]]()
        except KeyError:
            print "Comanda no coneguda!\n\n Ús: ./quechua.py start|stop|restart"
    else:
        print "Ús: ./quechua.py start|stop|restart"
        sys.exit(-1)

#~ def start_server():
    #~ pid = os.fork()
    #~ if pid == 0:
        #~ i = 0
        #~ while True:
            #~ try:
                #~ conn, addr = s.accept()
                #~ print "Conexión desde:", addr, "PID:", os.getpid()
                #~ respuesta(conn)
                #~ conn.close()
                #~ i += 1
                #~ if i == 1000: exit(0)
            #~ except socket.error:
                #~ pass
    #~ else:
        #~ return pid

#~ while True:
    #~ for i in range(5 - len(pids)):
        #~ pid = start_server()
        #~ pids.add(pid)
        #~ print "Nuevo proceso: ", pid

    #~ try:
        #~ (pid, status, rusage) = os.wait3(0)
        #~ if pid > 0:
            #~ pids.remove(pid)
    #~ except OSError: pass

    #~ print "acabó:", pid, "status:", status
