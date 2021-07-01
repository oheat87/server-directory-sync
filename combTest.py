import sys

import socket
import threading
from time import sleep

import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler

MAX_LISTEN = 5
MAX_BUFFER_LEN= 1024
IP_ADDR = '127.0.0.1'

class server_thread(threading.Thread):
    def __init__(self,name, socket):
        super().__init__()
        self.name = name
        self.server_socket=  socket

    def run(self):
        print('server thread start ', threading.currentThread().getName())
        print('waiting for client... ',threading.currentThread().getName())
        connection_socket,addr = self.server_socket.accept()
        print('access from',str(addr),'accepted')
        while True:
            data = connection_socket.recv(MAX_BUFFER_LEN)
            msg= data.decode('utf-8')
            if msg=='quit': break
            
            print('another server file modification:',msg)
            connection_socket.send('accepted'.encode('utf-8'))
            
        self.server_socket.close()
        print('server thread end ', threading.currentThread().getName())

class client_thread(threading.Thread):
    def __init__(self,name,ip_addr,port_num,targetDir):
        super().__init__()
        self.name = name
        self.ip_addr= ip_addr
        self.port_num= port_num
        self.client_socket=None
        self.targetDir=targetDir

    def run(self):
        print('client thread start ', threading.currentThread().getName())

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('trying to find server...','[',threading.currentThread().getName(),']')
        while True:
            try:
                self.client_socket.connect((self.ip_addr,self.port_num))
            except:
                sleep(0.001)
                continue
            break
        print('connected to server!','[',threading.currentThread().getName(),']')

        watcher=Watcher(self.client_socket,self.targetDir)
        watcher.run()
        while True:
##            print('you: ',end='')
##            msg= sys.stdin.readline().rstrip('\n')
##            if msg=='quit':
##                break
##            self.client_socket.sendall(msg.encode())
            try:
                response_msg = self.client_socket.recv(MAX_BUFFER_LEN).decode()
                if response_msg!='accepted':
                    print('error occurs sending message')
            except KeyboardInterrupt as e:
                try:
                    self.client_socket.shutdown(socket.SHUT_RDWR)
                except:
                    break
                break
            
        self.client_socket.close()
        print('client thread end ', threading.currentThread().getName())
    def getClientSocket(self):
        return self.client_socket
        
class Handler(FileSystemEventHandler):
    def __init__(self,client_socket):
        self.client_socket= client_socket
    def typeNameExtension(self,event):
        return_str=f'event type: {event.event_type}, '
        fname,ext=os.path.splitext(os.path.basename(event.src_path))
        return_str+=f'filename: {fname}, extension: {ext}'
        return return_str
    def on_created(self,event):
        self.client_socket.sendall(self.typeNameExtension(event).encode())
    def on_deleted(self,event):
        self.client_socket.sendall(self.typeNameExtension(event).encode())
    def on_modified(self,event):
        self.client_socket.sendall(self.typeNameExtension(event).encode())
    def on_moved(self,event):
        self.client_socket.sendall(self.typeNameExtension(event).encode())

class Watcher:
    def __init__(self,client_socket,path):
        print(f'now watching {path}')
        self.event_handler = Handler(client_socket)
        self.observer = Observer()
        self.target_dir= path
        self.currentDirectorySetting()

    def currentDirectorySetting(self):
        os.chdir(self.target_dir)
        print('first directory setting....')
        print(f'cwd: {os.getcwd()}')

    def run(self):
        self.observer.schedule(self.event_handler,self.target_dir,recursive=False)
        self.observer.start()
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt as e:
            print('shutting program')
            self.observer.stop()
            return


if __name__ == '__main__':
    #---------- server-client communication part
    send_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', int(sys.argv[1])))
    server_socket.listen(MAX_LISTEN)

    st= server_thread('ST',server_socket)
    st.start()

    ct= client_thread('CT',IP_ADDR,int(sys.argv[2]),sys.argv[3])
    ct.start()

    st.join()
    ct.join()
    print('end entire program')
