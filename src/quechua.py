#!/usr/bin/env python
# coding: utf-8

# AUTOR: Vicenç Juan Tomàs Montserrat
# LLICENCIA: GPL-3
# VERSIO: 0.1

##  @package quechua
#   Servidor web "estàtic" escrit en python

import socket
import os, sys, time
import sendfile
import ConfigParser
import logging

from stat import *

FILE_CONFIG = "../data/quechua.conf"

##  Llegeix la configuració de la variable del fitxer de configuració
#   @param clau
def read_config(clau):
    cfg = ConfigParser.ConfigParser()
    try:
        cfg.read([FILE_CONFIG])
        valor = cfg.get('quechuad', clau)
        return valor
    except IOError, ex:
        print "ERROR: El fitxer no se pot llegir!\n"
        print ex

##  Afegeix una nova variable al fitxer de configuració
#   @param clau Nom de la variable
#   @param valor Valor assignat a la clau
def set_config(clau, valor):
    cfg.set('quechuad', clau, valor)

##  Escriu els canvis que s'han produit
def write_config():
    try:
        f = open(FILE_CONFIG, 'w')
        config_parser.write(cfg)
        f.close()
    except IOError, ex:
        print "ERROR: El fitxer no se pot modificar!\n"
        print ex

    debug("Configuració guardada")

##  Mostra un missatge per pantalla amb la data i hora
#   @param message Missatge que es vol enregistrar
def debug(message):
    print "%s - %s" % (time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), message)

##  Envia missatges de log al fitxer de log corresponent
#   @param level Nivell de detall del missatge
#   @param message Missatge que es vol enregistrar
def log(level, message):
    """ escriu un missatge de log al fitxer de logs """
    logger.log(level, message)

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

##  Inicia el servidor
def start():
    logging.debug("prova debug")
    try:
        f = read_config('pid_file')
        fpid = open(f, 'r')
        fpid = int(fpid.read())
        print "El servidor ja està en marxa!, PID %s" % fpid.read()
        return
    except IOError:
        pass

    #debug("Servidor en marxa")
    # afegir codi a partir d'aqui

    pid = os.fork()
    if pid == 0:
        i = 0
        while True:
            try:
                conn, addr = s.accept()
                print "Conexió desde: ", addr, "PID: ", os.getpid()
                respuesta(conn)
                conn.close()
                i += 1
                if i == 1000: exit(0)
            except socket.error:
                pass
            except KeyboardInterrupt:
                stop()
    else:
        return pid

##  Atura el servidor correctament
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

        print "Aturant...", os.getpid()
    except IOError:
        print "El servidor ja està aturat!"

##  Reinicia el servidor
def restart():
    stop()
    time.sleep(1)
    start()

##  Inicia el servei de logging
def init_logger():
    logger = logging.getLogger('quechua')
    log = read_config('log_file')
    hdlr = logging.FileHandler(log)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)

dr = read_config('document_root')
env = os.getenv(dr)
lang = os.getenv('LANG')

if env:
    if lang.startswith('es'):
        document_root = env.strip() + '/Escritorio'
        print document_root
    elif lang.startswith('en'):
        document_root = env.strip() + '/Desktop'
else:
    print "ERROR: Variable d'entorn %s no definida!" %env
    sys.exit(-1)

##  Punt d'inici del programa
if __name__ == '__main__':
    # comprovacions
    if os.geteuid() != 0:
        print 'Has d''esser root! (o sudo)!'
        sys.exit(-1)

    if len(sys.argv) == 2:
        init_logger()

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            host = read_config('host')
            port = read_config('port')

            s.bind((host, int(port)))
            s.listen(1)
        except KeyboardInterrupt:
            print "\nSortint... ara!\n"
            sys.exit(-1)
        finally:
            s.close()

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

    n_procs = read_config('max_processes')

    # Inici
    while True:
        for i in range(int(n_procs)):
            pid = start()
            pids.add(pid)
            print "Nou proces: ", pid

        try:
            (pid, status, rusage) = os.wait3(0)
            if pid > 0:
                pids.remove(pid)
        except OSError:
            pass
        except KeyboardInterrupt:
            print "\nSortint... ara!\n"
            sys.exit(-1)

        print "ha acabat:", pid, "stat:", status
