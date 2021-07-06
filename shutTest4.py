import sys

#modules for socket communication
import socket
import threading
from time import sleep

#modules for file system tracking
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler

#some constants
MAX_LISTEN = 100
MAX_BUFFER_LEN= 1024
##IP_ADDR = '192.168.2.53'
IP_ADDR = '127.0.0.1'

#class for server threading
class server_thread(threading.Thread):
    def __init__(self,name, socket):
        super().__init__()
        self.name = name
        self.server_socket=  socket
        self.connection_socket=None

    def run(self):
        # run server thread by listening to server listening socket and
        # by responding to connection socket
        print('[server thread] start ', threading.currentThread().getName())
        try:
            while True:
                self.connection_socket,addr = self.server_socket.accept()
                print('[server thread] access from',str(addr),'accepted')

                data = self.connection_socket.recv(MAX_BUFFER_LEN)
                msg= data.decode('utf-8')
                print('[server thread] another server file modification:',msg)

                self.connection_socket.close()
                self.connection_socket=None
        except socket.error as e:
            print('[server thread] socket error debug:',e)
            print('[server thread] exiting....')

        # before finishing, close all the sockets this server thread has
        self.closeAllSocket()
        print('[server thread] end ', threading.currentThread().getName())
    def stop(self):
        # stop server thread by closing all the sockets that this thread has
        self.closeAllSocket()
    def closeAllSocket(self):
        # method for close all sockets that this server thread has
        # first, close server listening socket
        try:
            if self.server_socket.fileno()>=0:
                self.server_socket.close()
                print('[server thread] server socket closed')
        except socket.error as e:
            print('[server thread] server socket has already been closed')
            print('[server thread] exception content:',e)
        # second, close server connection socket
        try:
            if self.connection_socket is not None and self.connnection_socket.fileno()>=0:
                self.connection_socket.close()
                print('[server thread] server connection socket closed')
        except socket.error as e:
            print('[server thread] connection socket has already been closed')
            print('[server thread] exception content:',e)

# class for defining file system event handler
class Handler(FileSystemEventHandler):
    def __init__(self,ip_addr,port_num):
        self.ip_addr=ip_addr
        self.port_num= port_num
        pass
    def typeNameExtension(self,event):
        # function for get a full string that expresses what happened to folder
        return_str=f'event type: {event.event_type}, '
        fname,ext=os.path.splitext(os.path.basename(event.src_path))
        return_str+=f'filename: {fname}, extension: {ext}'
        return return_str
    #------------------from here to below, all functions works very similarly
    #------------------all they do is to catch specific event and send packet to server
    def on_created(self,event):
        client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            client_socket.connect((self.ip_addr,self.port_num))
            client_socket.sendall(self.typeNameExtension(event).encode())
        except socket.error as e:
            print('[filesystem event handler] socket error occurred:',e)
        client_socket.close()
    def on_deleted(self,event):
        client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            client_socket.connect((self.ip_addr,self.port_num))
            client_socket.sendall(self.typeNameExtension(event).encode())
        except socket.error as e:
            print('[filesystem event handler] socket error occurred:',e)
        client_socket.close()
    def on_modified(self,event):
        client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            client_socket.connect((self.ip_addr,self.port_num))
            client_socket.sendall(self.typeNameExtension(event).encode())
        except socket.error as e:
            print('[filesystem event handler] socket error occurred:',e)
        client_socket.close()
    def on_moved(self,event):
        client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            client_socket.connect((self.ip_addr,self.port_num))
            client_socket.sendall(self.typeNameExtension(event).encode())
        except socket.error as e:
            print('[filesystem event handler] socket error occurred:',e)
        client_socket.close()

#class for watching a folder
class Watcher:
    def __init__(self,path,ip_addr,port_num):
        
        self.event_handler = Handler(ip_addr,port_num)
        self.observer = Observer()
        self.target_dir= path
        os.chdir(path)
        print(f'[filesystem watcher] now watching {os.getcwd()}')

    def currentDirectorySetting(self):
        #function for change current working directory
        os.chdir(self.target_dir)
        print('[filesystem watcher] first directory setting....')
        print(f'[filesystem watcher] cwd: {os.getcwd()}')

    def run(self):
        #function for running filesystem watcher
        self.observer.schedule(self.event_handler,self.target_dir,recursive=False)
        self.observer.start()
        #keep watching a folder until a keyboard interrupt comes
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt as e:
            print('[filesystem watcher] exiting program...')
            self.observer.stop()
            return


if __name__ == '__main__':
    # check system arguments num
    if len(sys.argv)!=4:
        print('wrong system arguments!')
        sys.exit(1)
        
    #---------- server-client communication part
    server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', int(sys.argv[1])))
    server_socket.listen(MAX_LISTEN)

    st= server_thread('ST',server_socket)
    st.start()

    #---------- filesystem watcher part
    watcher= Watcher(sys.argv[3],IP_ADDR,int(sys.argv[2]))
    watcher.run()
    
    st.stop()
    st.join()
    print('[main thread] end entire program')
