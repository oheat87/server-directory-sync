"""
    이 코드는 WAIT!

    2주차에 수정진행 하다가 3주차에 최종수정하여 통합할 예정

"""

import sys

import socket
import threading
from time import sleep

import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

MAX_LISTEN = 100
MAX_BUFFER_LEN = 1024
IP_ADDR = '127.0.0.1'


class server_thread(threading.Thread):
    def __init__(self, name, socket, targetDir):
        super().__init__()
        self.name = name
        self.server_socket = socket
        self.connection_socket=None
        self.targetDir = targetDir

    def send(self):
        pass

    def receive(self):
        pass

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



                msg = msg.split(" ")  # msg[0]:type, msg[1]:filename
                # print(msg)

                if msg[0] == 'modified': continue

                print('another server file modification:', msg)

                if msg[0] == 'created':
                    print("UPLOAD 진행")
                    with open(msg[1], 'wb') as f:
                        data = self.connection_socket.recv(MAX_BUFFER_LEN)
                        print(data)
                        while data:
                            f.write(data)  # 1024바이트를 write
                            data = self.connection_socket.recv(MAX_BUFFER_LEN)
                            print("전송중...")

                else:
                    continue

            self.connection_socket.close()
            self.connection_socket = None
            print('server thread end ', threading.currentThread().getName())
        except socket.error as e:
            print('[server thread] socket error debug:', e)
            print('[server thread] exiting....')

        # before finishing, close all the sockets this server thread has

        self.closeAllSocket()
        print('[server thread] end ', threading.currentThread().getName())

    # =========================================================
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

    def getFileName(self, event):
        fname, ext = os.path.splitext(os.path.basename(event.src_path))
        filename = fname + ext
        print(filename)
        return filename

    #------------------from here to below, all functions works very similarly
    #------------------all they do is to catch specific event and send packet to server
    def on_created(self,event):
        client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            client_socket.connect((self.ip_addr,self.port_num))
            filename=self.getFileName(event)
            client_socket.sendall((event.event_type + " " + filename).encode())

            # =================================================================================
            if not filename:
                print("파일 %s (이)가 존재하지 않습니다" % filename)

            with open(filename, 'rb') as f:
                try:
                    data = f.read(MAX_BUFFER_LEN)
                    print(data)
                    while data:
                        client_socket.sendall(data)
                        data = f.read(MAX_BUFFER_LEN)
                except Exception as ex:
                    print(ex)


        except socket.error as e:
            print('[filesystem event handler] socket error occurred:',e)
        client_socket.close()
    def on_deleted(self,event):
        client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            client_socket.connect((self.ip_addr,self.port_num))
            client_socket.sendall((event.event_type + " " + self.getFileName(event)).encode())
        except socket.error as e:
            print('[filesystem event handler] socket error occurred:',e)
        client_socket.close()
    def on_modified(self,event):
        client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            client_socket.connect((self.ip_addr,self.port_num))
            client_socket.sendall((event.event_type + " " + self.getFileName(event)).encode())
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

class Watcher:
    def __init__(self, path,ip_addr,port_num):
        # print(f'now watching {path}')
        self.event_handler = Handler(ip_addr, port_num)
        self.observer = Observer()
        self.target_dir = path
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

    # check directory or not
    if (os.path.isdir(sys.argv[3]) == False):
        print("This directory is not exist")
        sys.exit()

    # ---------- server-client communication part
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', int(sys.argv[1])))
    server_socket.listen(MAX_LISTEN)

    st = server_thread('ST', server_socket, sys.argv[3])
    st.start()

    # ---------- filesystem watcher part
    watcher = Watcher(sys.argv[3], IP_ADDR, int(sys.argv[2]))
    watcher.run()

    st.stop()
    st.join()

    print('end entire program')

