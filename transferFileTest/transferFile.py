import sys

import socket
import threading
from time import sleep

import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

MAX_LISTEN = 5
MAX_BUFFER_LEN = 1024
IP_ADDR = '127.0.0.1'


class server_thread(threading.Thread):
    def __init__(self, name, socket, targetDir):
        super().__init__()
        self.name = name
        self.server_socket = socket
        self.targetDir = targetDir

    def send(self):
        pass

    def receive(self):
        pass

    def run(self):
        print('server thread start ', threading.currentThread().getName())
        print('waiting for client... ', threading.currentThread().getName())
        connection_socket, addr = self.server_socket.accept()
        print('access from', str(addr), 'accepted')
        try:
            while True:
                data = connection_socket.recv(MAX_BUFFER_LEN)
                data_transferred = 0
                msg = data.decode('utf-8')

                # if msg=='quit': break

                msg = msg.split(" ")  # msg[0]:type, msg[1]:filename
                # print(msg)

                if msg[0] == 'modified': continue

                print('another server file modification:', msg)

                # 다운로드 요청을 받음 =========================================================
                # 파일을 찾아서 해당파일을 타 서버로 전송
                # if msg[0] == 'download':
                #    with open(msg[1], 'rb') as f:
                #        try:
                #            data = f.read(MAX_BUFFER_LEN)
                #            # print(data)
                #            while data:
                #                connection_socket.send(data)
                #                data = f.read(MAX_BUFFER_LEN)
                #        except Exception as ex:
                #            print(ex)
                #    print("새 %s 파일 전송 완료! " % msg[1])
                #    # connection_socket.close()

                # 업로드를 요청 ===============================================================
                # 타 서버에서 보내온 파일을 저장
                if msg[0] == 'upload':
                    print("UPLOAD 진행")
                    with open(msg[1], 'wb') as f:
                        data = connection_socket.recv(MAX_BUFFER_LEN)
                        print(data)
                        while data:
                            f.write(data)  # 1024바이트를 write
                            data = connection_socket.recv(MAX_BUFFER_LEN)
                            print("전송중...")
                    print("파일 전송 완료. 전송량 %d" % (data_transferred))


                # =================================================================================

                # 파일이 삭제될 때 =================================================================
                # if (msg[0]=='deleted') & (os.path.exists(msg[1])):
                #    os.remove(self.targetDir+"\\"+msg[1])
                #    print("파일 %s (이)가 삭제되었습니다."%msg[1])
                # ================================================================================
                else:
                    continue

            self.server_socket.close()
            print('server thread end ', threading.currentThread().getName())
        except KeyboardInterrupt:
            self.server_socket.close()
            print("종료!!!")


class client_thread(threading.Thread):
    def __init__(self, name, ip_addr, port_num, targetDir):
        super().__init__()
        self.name = name
        self.ip_addr = ip_addr
        self.port_num = port_num
        self.client_socket = None
        self.targetDir = targetDir

    def run(self):
        print('client thread start ', threading.currentThread().getName())

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('trying to find server...', '[', threading.currentThread().getName(), ']')
        try:
            while True:
                try:
                    self.client_socket.connect((self.ip_addr, self.port_num))
                except:
                    sleep(0.001)
                    continue
                break
        except KeyboardInterrupt:
            os._exit(1)
        print('connected to server!', '[', threading.currentThread().getName(), ']')

        watcher = Watcher(self.client_socket, self.targetDir)
        # watcher.run()

        try:

            while True:

                print("upload 할 파일 이름: ")
                filename = input()
                if filename == "exit":
                    sys.exit()

                self.client_socket.sendall(filename.encode())
                filename = filename.encode().split(b' ')

                try:
                    # ===================================================================
                    # 서버에 파일을 다운로드 요청
                    # if filename[0]==b'download':
                    #    data = self.client_socket.recv(MAX_BUFFER_LEN)
                    #    # ========================================
                    #    # response_msg -> file
                    #    data_transferred=0
                    #    if not data:
                    #        print("파일 %s (이)가 존재하지 않습니다" %data)
                    #        # sys.exit()
                    #    with open(filename[1],'wb') as f:
                    #        try:
                    #            data = self.client_socket.recv(MAX_BUFFER_LEN)
                    #            # print(data)
                    #            while data:
                    #                f.write(data)   # 1024바이트를 write
                    #                # data_transferred+=len(data)
                    #                data=self.client_socket.recv(MAX_BUFFER_LEN)
                    #            f.close()
                    #        except Exception as ex:
                    #            print(ex)
                    #    print("파일 전송 완료. 전송량 - " )

                    # ===================================================================
                    # 서버로 파일을 업로드
                    if filename[0] == b'upload':
                        # data = self.client_socket.recv(MAX_BUFFER_LEN).decode()
                        # ========================================
                        # response_msg -> file
                        # data_transferred = 0
                        if not filename[1]:
                            print("파일 %s (이)가 존재하지 않습니다" % data)

                        with open(filename[1], 'rb') as f:
                            try:
                                data = f.read(MAX_BUFFER_LEN)
                                print(data)
                                while data:
                                    self.client_socket.sendall(data)
                                    data = f.read(MAX_BUFFER_LEN)
                            except Exception as ex:
                                print(ex)
                        # print("파일 전송 완료. 전송량 %d" % (data_transferred))

                    # if data!='accepted':
                    #    print('error occurs sending message')
                except KeyboardInterrupt as e:
                    try:
                        self.client_socket.shutdown(socket.SHUT_RDWR)
                    except:
                        break
                    break
        except KeyboardInterrupt as e:
            self.client_socket.close()
            print("종료")
            sys.exit()

        self.client_socket.close()
        print('client thread end ', threading.currentThread().getName())

    def getClientSocket(self):
        return self.client_socket


class Handler(FileSystemEventHandler):
    def __init__(self, client_socket):
        self.client_socket = client_socket

    def typeNameExtension(self, event):
        return_str = f'event type: {event.event_type}, '
        fname, ext = os.path.splitext(os.path.basename(event.src_path))
        return_str += f'filename: {fname}, extension: {ext}'
        return return_str

    def getFileName(self, event):
        fname, ext = os.path.splitext(os.path.basename(event.src_path))
        filename = fname + ext
        print(filename)
        return filename

    def on_created(self, event):
        self.client_socket.sendall((event.event_type + " " + self.getFileName(event)).encode())

    def on_deleted(self, event):
        self.client_socket.sendall((event.event_type + " " + self.getFileName(event)).encode())

    def on_modified(self, event):
        self.client_socket.sendall(event.event_type.encode())

    def on_moved(self, event):
        self.client_socket.sendall(self.typeNameExtension(event).encode())


class Watcher:
    def __init__(self, client_socket, path):
        print(f'now watching {path}')
        # self.event_handler = Handler(client_socket)
        self.client_socket = client_socket
        self.observer = Observer()
        self.target_dir = path
        self.currentDirectorySetting()

    def currentDirectorySetting(self):
        os.chdir(self.target_dir)
        print('first directory setting....')
        print(f'cwd: {os.getcwd()}')

    def run(self):
        # self.observer.schedule(self.event_handler,self.target_dir,recursive=False)
        # self.observer.start()

        try:
            while True:
                sleep(1)
        except KeyboardInterrupt as e:
            print('shutting program')
            self.observer.stop()
            return


def checkTerminate(st, ct):
    try:
        pass
    except KeyboardInterrupt:
        st.terminate()
        ct.terminate()
        print("프로그램 종료")
        sys.exit(1)


if __name__ == '__main__':
    try:
        # check directory or not
        if (os.path.isdir(sys.argv[3]) == False):
            print("This directory is not exist")
            sys.exit()

        # ---------- server-client communication part
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', int(sys.argv[1])))
        server_socket.listen(MAX_LISTEN)

        st = server_thread('ST', server_socket, sys.argv[3])
        ct = client_thread('CT', IP_ADDR, int(sys.argv[2]), sys.argv[3])

        st.daemon = False  # parent
        ct.daemon = True  # child

        try:

            st.start()
            ct.start()

            st.join()
            ct.join()

        except KeyboardInterrupt:
            print("exit")
            os._exit(1)

        print('end entire program')
    except (KeyboardInterrupt, SystemExit):
        print("종료")
        os._exit(1)
