"""
    update: 2021/07/08

    initialize folder structure for install (프로그램 설치를 위한 폴더구조 초기화)

    구현내용:
    1. synchronize the files by the filename (파일이름을 비교하여 파일구조 초기화)
    2. write the changes in the log file (초기화를 위해 발생한 파일 변경을 로그로 남김)

"""

import sys

# modules for socket communication
import socket
import threading
from time import sleep

# modules for file system tracking
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler

# modules for install program
import ast
import _init
import _logger

install = False  # 일단은 global변수로 선언하고 json설정파일에 프로그램 설정여부를 체크하는 flag넣기
install_log = _logger.make_logger('install')


#some constants
MAX_LISTEN = 100
MAX_BUFFER_LEN= 1024
##IP_ADDR = '192.168.2.60'
IP_ADDR = '127.0.0.1'

#class for server threading
class server_thread(threading.Thread):
    def __init__(self,name, socket, target_dir):
        super().__init__()
        self.name = name
        self.server_socket=socket
        self.target_dir=target_dir
        self.connection_socket=None

    def run(self):
        # run server thread by listening to server listening socket and
        # by responding to connection socket
        print('[server thread] start ', threading.currentThread().getName())
        try:
            while True:
                self.connection_socket,addr = self.server_socket.accept()
                print('[server thread] access from',str(addr),'accepted')

                data = self.connection_socket.recv(MAX_BUFFER_LEN).decode()
                print('[server thread] get file list from another server:',data)

                # install ===================================================================
                # pre file check:
                filelist=os.listdir(self.target_dir)
                data=ast.literal_eval(data)
                diff=set(data).difference(set(filelist))
                # print(list(diff))
                diff=list(diff)
                if len(diff)!=0:
                    # 여기서 diff 결과를 상대방에게 전달하여 없는 파일을 서버로 전송될 수 있게
                    file=diff[0]
                    self.connection_socket.send(file.encode())
                    changeState="create"
                    with open(file, 'wb') as f:
                        while True:
                            data = self.connection_socket.recv(MAX_BUFFER_LEN)
                            if not data:
                                print(f"sync file [{file}] from server")
                                # format: filename - state
                                install_log.info(f"{file} - {changeState}")
                                break
                            f.write(data)
                    #self.connection_socket.close()
                    #self.connection_socket = None
                    # =======================================================================
                if len(diff)==0:
                    break
        except socket.error as e:
            print('[server thread] socket error debug:',e)
            print('[server thread] exiting....')

        # before finishing, close all the sockets this server thread has
        self.closeAllSocket()
        print('[server thread] end ', threading.currentThread().getName())

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
            if self.connection_socket is not None and self.connection_socket.fileno()>=0:
                self.connection_socket.close()
                print('[server thread] server connection socket closed')
        except socket.error as e:
            print('[server thread] connection socket has already been closed')
            print('[server thread] exception content:',e)

    def stop(self):
        # stop server thread by closing all the sockets that this thread has
        self.closeAllSocket()

"""
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
"""

class Install:
    def __init__(self,path,ip_addr,port_num):
        self.ip_addr=ip_addr
        self.port_num=port_num
        self.target_dir=path
        os.chdir(path)
        print(f'[Install] directory path: {os.getcwd()}')

    def install(self):

        while True:
            connect = False
            while not connect:
                try:
                    install_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    install_socket.connect((self.ip_addr,self.port_num))
                    connect=True
                except ConnectionRefusedError: # 서버 연결 열릴 때 까지 대기
                    continue

            install_socket.sendall(str(os.listdir(self.target_dir)).encode())

            file = install_socket.recv(MAX_BUFFER_LEN) # 파일이름 받아옴
            print(f"send file [{file}] to server")
            if not file:
                break
            try:
                with open(file.decode(), 'rb') as f:
                    while True:
                        data = f.read(MAX_BUFFER_LEN)
                        if not data:
                            break
                        install_socket.sendall(data)
                install_socket.close()
            except OSError as e:
                print('there is no such file:', e)
            except KeyboardInterrupt:
                os._exit(0)
        # ==========================================================================

if __name__ == '__main__':

    # set install directory path
    # print("설치할 위치 지정:")
    # install_path=input()
    # _init.create(install_path)

    # check system arguments num
    if len(sys.argv)!=4:
        print('wrong system arguments!')
        sys.exit(1)
        
    #---------- server-client communication part
    server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', int(sys.argv[1])))
    server_socket.listen(MAX_LISTEN)

    st= server_thread('ST',server_socket,sys.argv[3])
    st.start()

    #---------- filesystem watcher part
    try:
        if install==False:
            install=Install(sys.argv[3],IP_ADDR,int(sys.argv[2]))
            install.install()
            install=True
            print("[install status] success!")
    except KeyboardInterrupt:
        os._exit(0)

    # watcher = Watcher(sys.argv[3], IP_ADDR, int(sys.argv[2]))
    # watcher.run()
    
    #st.stop()
    st.join()
    print('[main thread] end entire program')
