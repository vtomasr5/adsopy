#!/usr/bin/env python
# coding: utf-8

import socket
import os, sys, time
import sendfile
import ConfigParser
import logging

from stat import *

FILE_CONFIG = "../data/quechua.conf"

def read_config(seccio, clau):
    cfg = ConfigParser.ConfigParser()
    try:
        cfg.read([FILE_CONFIG])
        valor = cfg.get(seccio, clau)
        return valor
    except IOError, ex:
        print "ERROR: Es fitxer no se pot llegir!\n"
        print ex

def set_config(seccio, clau, valor):
    cfg.set(seccio, clau, valor)

def write_config():
    try:
        f = open(FILE_CONFIG, 'w')
        config_parser.write(cfg)
        f.close()
    except IOError, ex:
        print "ERROR: Es fitxer no se pot escriure!\n"
        print ex

    debug("Configuració guardada")

def debug(message):
    print "%s - %s" % (time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), message)

def log(level, message):
    """ escriu un missatge de log al fitxer de logs """
    logger.log(level, message)

def start():
    logging.debug("prova debug")
    try:
        f = open(config.PID_FILE, 'r')
        fpid = open(f, 'r')
        fpid = int(fpid.read())
        print "El servidor ja està en marxa, PID %s!" % fpid.read()
        return
    except:
        print "Arrancant..."
    finally:
        fpid.close()

    debug("Servidor en marxa")
    # afegir codi a partir d'aqui

def stop():
    try:
        f = read_config('quechuad', 'pid_file')
        fpid = open(f, 'r')
        fpid = int(fpid.read())

        while True:
            try:
                os.kill(fpid, signal.SIGTERM)
            except OSError: # cutre?
                break
            time.sleep(0.2)

        print "Aturat!"
    except IOError:
        print "El servidor ja està aturat!"
    finally:
        fpid.close()

def restart():
    stop()
    time.sleep(1)
    start()

def init_logger():
    logger = logging.getLogger('quechua')
    log = read_config('quechuad', 'log_file')
    hdlr = logging.FileHandler(log)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        init_logger()
        try:
            {'start': start,
             'stop': stop,
             'restart': restart}[sys.argv[1]]()
        except KeyError:
            print "Comanda no coneguda!\n\n ús: quechua.py start|stop|restart"

    else:
        print "ús: quechua.py start|stop|restart"
        sys.exit(-1)


#~ def respuesta(sock):
    #~ try:
        #~ OUT = sock.makefile()
        #~ http_command = OUT.readline()
        #~ headers = []
        #~ command = http_command.split()
        #~ print "Commando:", command
        #~ for line in OUT:
            #~ if line.strip() == "": break
            #~ headers.append(line)
        #~ if command[0] == "GET":
            #~ if command[1] == "/":
                #~ filename = document_root + "/index.html"
            #~ else:
                #~ filename = document_root + command[1]
            #~ try:
                #~ FILE = open(filename, "rb")
                #~ print "Sending", filename
                #~ size = os.stat(filename)[ST_SIZE]
                #~ OUT.write("HTTP/1.0 200 Va be\r\n")
                #~ OUT.write("Content-Length: %d\r\n\r\n" % size)
                #~ OUT.flush()
                #~ sendfile.sendfile(OUT.fileno(), FILE.fileno(), 0, size)
#~
            #~ except IOError:
                #~ OUT.write("HTTP 404 Fichero no existe\r\n")
                #~ print "Error con", filename
    #~ except Exception, e:
            #~ print "Error en la conexión", e
    #~ OUT.close()
#~
#~ s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#~ s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#~
#~ s.bind(("", 10000))
#~ s.listen(1)
#~
#~ pids = set()
#~
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
#~
#~ while True:
    #~ for i in range(5 - len(pids)):
        #~ pid = start_server()
        #~ pids.add(pid)
        #~ print "Nuevo proceso: ", pid
#~
    #~ try:
        #~ (pid, status, rusage) = os.wait3(0)
        #~ if pid > 0:
            #~ pids.remove(pid)
    #~ except OSError: pass
#~
    #~ print "acabó:", pid, "status:", status
#~
