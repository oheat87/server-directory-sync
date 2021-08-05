"""
    update: 2021/07/16

    initialize folder structure for install (프로그램 설치를 위한 폴더구조 초기화)

    구현내용:
    1. synchronize the files by the filename (파일이름을 비교하여 파일구조 초기화)
    2. write the changes in the log file (초기화를 위해 발생한 파일 변경을 로그로 남김)
    3. ignore sub-folders (default: 폴더내의 하위폴더들은 ignore 되게..)
    4. add _logtojson module (.log파일을 .json파일로 parsing)
    5. add setting.json (json파일로 설정값 저장, install은 최초 한번만 실행)
    6. add log2json function in _logtojson (여러개의 log를 .json으로 파싱)
    7. set the install path by user and store the log in /syncPro/log (설치위치 지정 및 로그폴더에 로그저장)

    +8. change the name format (2021-07-15.json) (날짜.json으로 로그파일 이름변경)
    +9. merge _init and _install (_install모듈로 통합)

"""

import sys

# modules for socket communication
import socket
import threading

###
import recursiveTest
###

from time import sleep

# modules for file system tracking
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler

# modules for install program
import json

import _logtojson
import _install

install = False  # 일단은 global변수로 선언하고 json설정파일에 프로그램 설정여부를 체크하는 flag넣기

# some constants
MAX_LISTEN = 100
MAX_BUFFER_LEN = 1024
# IP_ADDR = '192.168.2.60'
# IP_ADDR = '127.0.0.1'

# class for server threading
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
            self.connection_socket, addr = self.server_socket.accept()
            print('[server thread] access from', str(addr), 'accepted')


            # 수정: 하위폴더가 존재할 시, 하위폴더 우선 동기화
            ##########################################
            your_dict=self.connection_socket.recv(MAX_BUFFER_LEN).decode()
            your_dict=your_dict.replace("null","None")
            your_dict=eval(your_dict)
            my_dict={}
            recursiveTest.getDirTree(self.target_dir,my_dict)


            my_file_list=[]
            my_dir_list=[] # no need to send
            recursiveTest.dfs(my_dict,my_file_list,my_dir_list)

            your_file_list=[]
            your_dir_list=[]
            recursiveTest.dfs(your_dict,your_file_list,your_dir_list)

            # print(your_file_list)
            # print(my_file_list)

            file_list=list(set(your_file_list)-set(my_file_list))


            ### MAKE DIR ###
            for item in your_dir_list:
                path=os.path.join(self.target_dir,item)
                if not os.path.exists(path):
                    # print("[MAKE DIR] @ ",path)
                    os.mkdir(path)
            ### ###
            self.connection_socket.close()
            self.connection_socket = None

            for i in range(len(file_list)):
                # SOCKET
                self.connection_socket, addr = self.server_socket.accept()
                print('[server thread] access from', str(addr), 'accepted')


                file=file_list[i]
                self.connection_socket.send(file.encode())
                changeState="c" # create
                filepath=os.path.join(self.target_dir,file)
                with open(filepath, 'wb') as f:
                    while True:
                        data = self.connection_socket.recv(MAX_BUFFER_LEN)
                        if not data:
                            print(f"sync file [{file}] from server")
                            # format: filename - state
                            _install.install_log.info(f"{file}{changeState}")
                            break
                        f.write(data)
                self.connection_socket.close()
                self.connection_socket = None
                # print("GO!")
                # =======================================================================

                # self.connection_socket.close()
                # self.connection_socket = None

        except socket.error as e:
            print('[server thread] socket error debug:',e)
            print('[server thread] exiting....')

        # re-start
        install_path = os.path.join(os.getcwd(),"syncPro")
        if os.path.exists(os.path.join(install_path,"setting.json")):
            with open(os.path.join(install_path,"setting.json"), 'r') as f:
                setting = json.load(f)
            if setting["install"]==True:
                _logtojson.json2log()

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
def main(port1,ip2,port2,syncpath,interval):
    global install_path
    # check system arguments num
    # if len(sys.argv) != 4:
    #     print('wrong system arguments!')
    #     sys.exit(1)

    # install & setting ========================================================

    # set install directory path
    install_path=os.getcwd()
    log_path=os.path.join(install_path , 'syncPro' , 'log')
    _install.initFolder(install_path)
    print(os.getcwd())

    # setFile = install_path + '\\syncPro\\setting.json'
    install=_install.Install(syncpath,'localhost',port1,install_path)

    # with open(setFile, 'r') as f:
    #     setting = json.load(f)
    # ==========================================================================

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', int(port1)))
    server_socket.listen(MAX_LISTEN)

    st = server_thread('ST', server_socket, syncpath)
    st.start()

    ##
    install.initSet(ip2,int(port2),interval)
    ##
    print("DEBUG ========================== ")

    # watcher = Watcher(sys.argv[3], IP_ADDR, int(sys.argv[2]))
    # watcher.run()

    #st.stop()
    st.join()
    print('[main thread] end entire program')

    return log_path

if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2],sys.argv[3])
