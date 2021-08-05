import sys
import os

import random

#modules for socket communication
import socket
import threading
import time

#JSON
import json

#some constants
MAX_LISTEN = 100
MAX_BUFFER_LEN= 1024
##IP_ADDR = '192.168.2.53'
IP_ADDR = '127.0.0.1'

RANCHAR_LEN=20

#debug constants
DEBUG_PORT=3500
DEBUG_IP_ADDR='127.0.0.1'
DEBUG_PATH='C:\\Users\\한태호\\Documents\\pyRepos\\dsTest\\testFolder'

#class for server threading
class trackData_server_thread(threading.Thread):
    def __init__(self,name, socket,JSON_fname):
        super().__init__()
        self.name = name
        self.server_socket=  socket
        self.connection_socket=None
        self.JSON_fname=JSON_fname

    def run(self):
        # run server thread by listening to server listening socket and
        # by responding to connection socket
        print('[trackData_server thread] start ', threading.currentThread().getName())
        try:
            while True:
                self.connection_socket,addr = self.server_socket.accept()
                print('[trackData_server thread] access from',str(addr),'accepted')

                with open(self.JSON_fname,'wb') as f:
                    while True:
                        data = self.connection_socket.recv(MAX_BUFFER_LEN)
                        if not data:
                            break
                        f.write(data)

                print('[trackData_server thread] JSON file receiving done')
                break
        except socket.error as e:
            print('[trackData_server thread] socket error debug:',e)
            print('[trackData_server thread] exiting....')
        except Exception as e:
            print('[server thread] error occured while receiving JSON file:',e)

        # before finishing, close all the sockets this server thread has
        self.closeAllSocket()
        print('[trackData_server thread] end ', threading.currentThread().getName())
##    def stop(self):
##        # stop server thread by closing all the sockets that this thread has
##        self.closeAllSocket()
    def closeAllSocket(self):
        # method for close all sockets that this server thread has
        # first, close server listening socket
        try:
            if self.server_socket.fileno()>=0:
                self.server_socket.close()
                print('[trackData_server thread] server socket closed')
        except socket.error as e:
            print('[trackData_server thread] server socket has already been closed')
            print('[trackData_server thread] exception content:',e)
        # second, close server connection socket
        try:
            if self.connection_socket is not None and self.connection_socket.fileno()>=0:
                self.connection_socket.close()
                print('[trackData_server thread] server connection socket closed')
        except socket.error as e:
            print('[trackData_server thread] connection socket has already been closed')
            print('[trackData_server thread] exception content:',e)

# get a random character which is one of [0-9A-Za-z]
def getRandomChar():
    code=random.randrange(62)
    if code<10: return chr(code+48)
    elif code<36: return chr(code-10+65)
    else: return chr(code-36+97)

# get a random JSON file name that doesn't exist in the current working directory
def getJSONName():
    baseName='data'
    ext='.json'
    for _ in range(RANCHAR_LEN):
        baseName+=getRandomChar()
    while os.path.exists(baseName+ext):
        baseName+=getRandomChar()
    return baseName+ext

# get a JSON file name as an argument, send it to other server and recieve a another JSON file
def exchangeTrackData(file_name, ip_addr, my_port_num, other_port_num):
    #---------- server part
    server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', my_port_num))
    server_socket.listen(MAX_LISTEN)

    received_fname= getJSONName()
    st= trackData_server_thread('ST',server_socket,received_fname)
    st.start()

    #---------- client part
    client_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client_socket.connect((ip_addr,other_port_num))
        except ConnectionRefusedError:
            time.sleep(0.001)
            continue
        break
    print('[newTmpTest xcgTD] server-client connection built')

    try:
        with open(file_name,'rb') as f:
            while True:
                data=f.read(MAX_BUFFER_LEN)
                if not data:
                    break
                client_socket.sendall(data)
        client_socket.close()
    except Exception as e:
        print('[newTmpTest xcgTD] error occured while sending JSON file:',e)
    st.join()

    return received_fname

def makeJSON(dictionary):
    JSON_fname=getJSONName()
    with open(JSON_fname,'w') as f:
        json.dump(dictionary,f)
    return JSON_fname

def loadJSON(file_name):
    with open(file_name) as f:
        dictionary_JSON=json.load(f)
    return dictionary_JSON

