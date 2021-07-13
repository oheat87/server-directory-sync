import os
import socket

MAX_BUFFER_LEN=1024

class Install:
    def __init__(self, path, ip_addr, port_num):
        self.ip_addr = ip_addr
        self.port_num = port_num
        self.target_dir = path
        os.chdir(path)
        print(f'[Install] directory path: {os.getcwd()}')


    def install(self):
        while True:
            connect = False
            while not connect:
                try:
                    install_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    install_socket.connect((self.ip_addr, self.port_num))
                    connect = True
                except ConnectionRefusedError:  # 서버 연결 열릴 때 까지 대기
                    continue

            filelist = os.listdir(self.target_dir)

            # 하위폴더 ignore
            for _ in filelist:
                if os.path.isdir(self.target_dir + '/' + _):
                    filelist.remove(_)

            install_socket.sendall(str(filelist).encode())

            file = install_socket.recv(MAX_BUFFER_LEN)  # 파일이름 받아옴
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