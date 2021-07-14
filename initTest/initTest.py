"""
    update: 2021/07/14

    initialize folder structure for install (프로그램 설치를 위한 폴더구조 초기화)

    구현내용:
    1. synchronize the files by the filename (파일이름을 비교하여 파일구조 초기화)
    2. write the changes in the log file (초기화를 위해 발생한 파일 변경을 로그로 남김)

    +3. ignore sub-folders (default: 폴더내의 하위폴더들은 ignore 되게..)
    +4. add _logtojson module (.log파일을 .json파일로 parsing)
    +5. add setting.json (json파일로 설정값 저장, install은 최초 한번만 실행)
    +6. add log2json function in _logtojson (여러개의 log를 .json으로 파싱)
    +7. set the install path by user and store the log in /syncPro/log (설치위치 지정 및 로그폴더에 로그저장)

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
import json

import _init
#import _logger
import _logtojson
import _install

install = False  # 일단은 global변수로 선언하고 json설정파일에 프로그램 설정여부를 체크하는 flag넣기

#some constants
MAX_LISTEN = 100
MAX_BUFFER_LEN= 1024
#IP_ADDR = '192.168.2.60'
IP_ADDR = '127.0.0.1'
DEFAULT_TIME_INTERVAL=120


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
                data=ast.literal_eval(data) #string->list, data:원격서버 파일리스트

                # 하위폴더 ignore
                for _ in data:
                    if os.path.isdir(self.target_dir+'/'+_):
                        data.remove(_)
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
                                _install.install_log.info(f"{file}/{changeState}")
                                break
                            f.write(data)
                    #self.connection_socket.close()
                    #self.connection_socket = None
                    # =======================================================================
                if len(diff)==0:
                    break
            # self.connection_socket.close()
            # self.connection_socket = None
        except socket.error as e:
            print('[server thread] socket error debug:',e)
            print('[server thread] exiting....')

        # json format
        _logtojson.log2json()

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

# ==========================================================================

if __name__ == '__main__':

    # check system arguments num
    if len(sys.argv) != 4:
        print('wrong system arguments!')
        sys.exit(1)

    # set install directory path
    print("설치할 위치 지정:")
    install_path=input()
    _logtojson.setLogDir(install_path + '\\syncPro\\log')
    _init.create(install_path)
    print(os.getcwd())

    # install & setting ========================================================
    setFile = install_path + '\\syncPro\\setting.json'
    install=_install.Install(sys.argv[3],'localhost',sys.argv[1],install_path)

    with open(setFile, 'r') as f:
        setting = json.load(f)
    # ==========================================================================

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', int(sys.argv[1])))
    server_socket.listen(MAX_LISTEN)

    st = server_thread('ST', server_socket, sys.argv[3])
    st.start()

    ##
    install.setting(IP_ADDR,int(sys.argv[2]))
    ##


    # watcher = Watcher(sys.argv[3], IP_ADDR, int(sys.argv[2]))
    # watcher.run()

    # st.stop()
    st.join()
    print('[main thread] end entire program')


# 초기화에 사용되지 않은 코드 =================================================================
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
