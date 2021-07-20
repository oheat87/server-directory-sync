import sys
import os

#modules for socket communication
import socket
import threading
import time

import _logtojson

#some constants
MAX_LISTEN = 100
MAX_BUFFER_LEN= 1024
##IP_ADDR = '192.168.2.53'
IP_ADDR = '127.0.0.1'
HANDSHAKE_STR_INIT='HANDSHAKE_SYNCJOB_INIT'
HANDSHAKE_STR_FILE='HANDSHAKE_SYNCJOB_FILE'
HANDSHAKE_STR_INIT_ACK='INIT_ACK'
HANDSHAKE_STR_FILE_ACK='FILE_ACK'

#debug constants
DEBUG_PORT=3500
DEBUG_IP_ADDR='127.0.0.1'
DEBUG_PATH='C:\\Users\\한태호\\Documents\\pyRepos\\dsTest\\testFolder'

#class for server threading
class files_server_thread(threading.Thread):
    def __init__(self,name, socket):
        super().__init__()
        self.name = name
        self.server_socket=  socket
        self.connection_socket=None
        self.recv_fno=None

    def run(self):
        # run server thread by listening to server listening socket and
        # by responding to connection socket
        print('[files_server thread] start ', threading.currentThread().getName())

        #handshaking part
        #get predefined handshaking string and receive the number of files being received
        try:
            while True:
                self.connection_socket,addr = self.server_socket.accept()

                # get handshaking message
                data = self.connection_socket.recv(MAX_BUFFER_LEN)
                msg = data.decode('utf-8')
                if msg!=HANDSHAKE_STR_INIT:
                    print(f'[files_server thread] received message: {msg}')
                    print(f'msg==HANDSHAKE_STR_INIT: {msg==HANDSHAKE_STR_INIT}')
                    self.connection_socket.close()
                    self.connection_socket=None
                    continue
                self.connection_socket.sendall(HANDSHAKE_STR_INIT_ACK.encode('utf-8'))

                # get the number of files receiving
                data = self.connection_socket.recv(MAX_BUFFER_LEN)
                self.recv_fno=int(data.decode('utf-8'))
                self.connection_socket.sendall(HANDSHAKE_STR_INIT_ACK.encode('utf-8'))

                self.connection_socket.close()
                self.connection_socket=None
                break
        except Exception as e:
            print('[files_server thread] error occured while handshaking')
            print(e)
            sys.exit(1)

        print(f'[files_server thread] handshake completed, fileno:{self.recv_fno}')

        #receiving files part
        #get predefined handshaking string, filename and then receive file
        recv_count=0
        try:
            while True:
                if recv_count==self.recv_fno:
                    break
                self.connection_socket,addr = self.server_socket.accept()

                # get handshaking message
                data = self.connection_socket.recv(MAX_BUFFER_LEN)
                msg= data.decode('utf-8')
                if msg!=HANDSHAKE_STR_FILE:
                    self.connection_socket.close()
                    self.connection_socket=None
                    continue
                self.connection_socket.sendall(HANDSHAKE_STR_FILE_ACK.encode('utf-8'))

                # get filename
                data = self.connection_socket.recv(MAX_BUFFER_LEN)
                file_name, file_flag= data.decode('utf-8').split('/')

                self.connection_socket.sendall(HANDSHAKE_STR_FILE_ACK.encode('utf-8'))

                # receive file
                with open(file_name,'wb') as f:
                    while True:
                        data = self.connection_socket.recv(MAX_BUFFER_LEN)
                        if not data:
                            break
                        f.write(data)

                ### save logs =====================================
                if file_flag=='c':changeState="create"
                elif file_flag=='m':changeState="modified"
                _logtojson.json2log()
                log_file, log_time = _logtojson.run('sync')
                log_file.info(f"{file_name}/{changeState}")
                ### re-format to .json
                _logtojson.log2json()
                ### ===========================================
                print(f'[files_server thread] {file_name} successfully received')

                self.connection_socket.close()
                self.connection_socket=None
                recv_count+=1
        except socket.error as e:
            print('[files_server thread] socket error debug:',e)
            print('[files_server thread] exiting....')
        except Exception as e:
            print('[files_server thread] error occured while receiving files')
            print(e)
            sys.exit(1)

        print(f'[files_server thread] file receiving completed')

        # before finishing, close all the sockets this server thread has
        self.closeAllSocket()
        print('[files_server thread] end ', threading.currentThread().getName())
    def stop(self):
        # stop server thread by closing all the sockets that this thread has
        self.closeAllSocket()
    def closeAllSocket(self):
        # method for close all sockets that this server thread has
        # first, close server listening socket
        try:
            if self.server_socket.fileno()>=0:
                self.server_socket.close()
                print('[files_server thread] server socket closed')
        except socket.error as e:
            print('[files_server thread] server socket has already been closed')
            print('[files_server thread] exception content:',e)
        # second, close server connection socket
        try:
            if self.connection_socket is not None and self.connection_socket.fileno()>=0:
                self.connection_socket.close()
                print('[files_server thread] server connection socket closed')
        except socket.error as e:
            print('[files_server thread] connection socket has already been closed')
            print('[files_server thread] exception content:',e)

def getJobList(my_event_dictionary,other_event_dictionary):
    deleteList=[]
    sendList=[]
    # my_modifiedList=[]
    recv_createList=[]
    recv_modifiedList=[]
    # first compare with respect to my file list
    for file_name in my_event_dictionary:
        if file_name not in other_event_dictionary:
            if my_event_dictionary[file_name][0]!='d':
                if my_event_dictionary[file_name][0]=='c':
                    sendList.append(file_name+"/c")
                if my_event_dictionary[file_name][0]=='m':
                    sendList.append(file_name+"/m")
        else:
            my_event=my_event_dictionary[file_name]
            other_event=other_event_dictionary[file_name]
            if my_event[0]=='d':
                #DEBUG: check if an impossible case has occured
                if not(other_event[0]=='d' or other_event[0]=='m'):
                    print('[syncJobTest getJobList func] unexpected pair of event has occured!')
                    print(f'my_event_dictionary[{file_name}][0]=\'{my_event[0]}\'')
                    print(f'other_event_dictionary[{file_name}][0]=\'{other_event[0]}\'')
                    sys.exit(1)
            elif my_event[0]=='m':
                if other_event[0]=='d':
                    deleteList.append(file_name)
                elif other_event[0]=='m':
                    if my_event[1]>other_event[1]:
                        sendList.append(file_name+"/m")
                    else:
                        # my_modifiedList.append(file_name)
                        recv_modifiedList.append(file_name)

                else:
                    print('[syncJobTest getJobList func] unexpected pair of event has occured!')
                    print(f'my_event_dictionary[{file_name}][0]=\'{my_event[0]}\'')
                    print(f'other_event_dictionary[{file_name}][0]=\'{other_event[0]}\'')
                    sys.exit(1)
            elif my_event[0]=='c':
                if other_event[0]=='c':
                    if my_event[1]>other_event[1]:
                        sendList.append(file_name+"/c")
                    else:
                        # my_modifiedList.append(file_name)
                        recv_modifiedList.append(file_name)

                else:
                    print('[syncJobTest getJobList func] unexpected pair of event has occured!')
                    print(f'my_event_dictionary[{file_name}][0]=\'{my_event[0]}\'')
                    print(f'other_event_dictionary[{file_name}][0]=\'{other_event[0]}\'')
                    sys.exit(1)
            else:
                print('[syncJobTest getJobList func] unexpected pair of event has occured!')
                print(f'my_event_dictionary[{file_name}][0]=\'{my_event[0]}\'')
                print(f'other_event_dictionary[{file_name}][0]=\'{other_event[0]}\'')
                sys.exit(1)

            # there is no need to double check files which are in both of the dictionaries
            # so, delete the entry in the other_event_dictionary not to double check
            del other_event_dictionary[file_name]


    # second compare with respect to other's file list
    for file_name in other_event_dictionary:
        if file_name not in my_event_dictionary:
            if other_event_dictionary[file_name][0]=='d':
                deleteList.append(file_name)
            elif other_event_dictionary[file_name][0] == 'm':
                recv_modifiedList.append(file_name)
            elif other_event_dictionary[file_name][0] == 'c':
                recv_createList.append(file_name)
            else:
                print('[syncJobTest getJobList func] unexpected pair of event has occured!')
                print(f'my_event_dictionary[{file_name}][0]=\'{my_event[0]}\'')
                print(f'other_event_dictionary[{file_name}][0]=\'{other_event[0]}\'')
                sys.exit(1)
            continue
        else:
            print('[syncJobTest getJobList func] unexpected pair of event has occured!')
            print(f'my_event_dictionary[{file_name}][0]=\'{my_event[0]}\'')
            print(f'other_event_dictionary[{file_name}][0]=\'{other_event[0]}\'')
            sys.exit(1)

    return [deleteList,sendList,recv_createList,recv_modifiedList]

def deleteFiles(file_list):
    for file_name in file_list:
        ### save logs =====================================
        changeState="delete"
        _logtojson.json2log()
        log_file, log_time = _logtojson.run('sync')
        log_file.info(f"{file_name}/{changeState}")
        ### re-format to .json
        _logtojson.log2json()
        ### ===============================================
        os.remove(file_name)

def exchangeFiles(file_list,ip_addr,my_port_num,other_port_num):
    print('[syncJobTest xcgFiles] start exchanging files!')
    #---------------server part
    server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', my_port_num))
    server_socket.listen(MAX_LISTEN)

    st= files_server_thread('ST',server_socket)
    st.start()
    
    #---------------client part
    #first, handshake with server 
    handshake_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    while True:
        try:
            handshake_socket.connect((ip_addr,other_port_num))
        except ConnectionRefusedError:
            time.sleep(0.001)
            continue
        break
    handshake_socket.sendall(HANDSHAKE_STR_INIT.encode('utf-8'))
    while True:
        try:
            handshake_socket.recv(MAX_BUFFER_LEN)
            break
        except ConnectionResetError:
            pass
    handshake_socket.sendall(str(len(file_list)).encode('utf-8'))
    while True:
        try:
            handshake_socket.recv(MAX_BUFFER_LEN)
            break
        except ConnectionResetError:
            pass
    handshake_socket.close()
    print('[syncJobTest xcgFiles] first handshaking done')
    
    #then, send files
    for file_name in file_list:
        client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        while True:
            try:
                client_socket.connect((ip_addr,other_port_num))
            except ConnectionRefusedError:
                time.sleep(0.001)
                continue
            break
        client_socket.sendall(HANDSHAKE_STR_FILE.encode('utf-8'))
        client_socket.recv(MAX_BUFFER_LEN)
        client_socket.sendall(file_name.encode('utf-8'))
        client_socket.recv(MAX_BUFFER_LEN)
        print(f'[syncJobTest xcgFiles] sending file {file_name}')

        try:
            file_name=file_name.split("/")[0]
            with open(file_name,'rb') as f:
                while True:
                    data=f.read(MAX_BUFFER_LEN)
                    if not data:
                        break
                    client_socket.sendall(data)
            client_socket.close()
        except Exception as e:
            print(f'[syncJobTest xcgFiles] error occured while sending {file_name}:',e)
    st.join()
