import os
import socket
import json
import _logtojson

MAX_BUFFER_LEN=1024

def initFolder(path):
    setting_format=json.dumps({
	"servers": [
		{
			"ip_1": "localhost",
			"port_1": None
		},
		{
			"ip_2": "",
			"port_2": None
		}
	],
	"dirPath": "",
	"timeInterval": "",
	"latestSync": "",
	"install": False
}, indent=4)

    try:
        if os.path.isdir(path):
            install_path=path+'\\syncPro'
            os.makedirs(install_path)
            os.makedirs(install_path+'\\backup')
            os.makedirs(install_path+'\\log')
            f=open(install_path+'\\setting.json','w')
            f.writelines(setting_format)
            f.close()
    except OSError:
            print('Error: Creating directory. ' + path)

class Install:
    def __init__(self, path, ip_addr, port_num, install_path):
        global install_log, time
        self.ip_addr = ip_addr
        self.port_num = int(port_num)
        self.target_dir = path
        self.install_path=install_path+'\\syncPro'
        install_log, time = _logtojson.run('install')
        os.chdir(path)
        print(f'[Install] directory path: {os.getcwd()}')

    def setting(self,ip2,port2):
        setFile = self.install_path + '\\setting.json'

        with open(setFile, 'r') as f:
            setting = json.load(f)

        if setting["install"] == False:
            setting["servers"][0]["ip_1"] = 'localhost'
            setting["servers"][0]["port_1"] = self.port_num

            setting["servers"][1]["ip_2"] = ip2
            setting["servers"][1]["port_2"] = port2

            setting["dirPath"] = self.target_dir

            with open(setFile, 'w', encoding='utf-8') as mk:
                json.dump(setting, mk, indent='\t')

        if setting["install"] == False:
            #install = Install(setting["dirPath"], setting["servers"][1]["ip_2"], int(setting["servers"][1]["port_2"]))
            self.install(ip2,port2)
            setting["install"] = True
            setting["latestSync"]=time
            # update json seeting file
            with open(setFile, 'w', encoding='utf-8') as mk:
                json.dump(setting, mk, indent='\t')

            # json format
            # _logtojson.log2json()

            print("[install status] success!")

    def install(self,ip2,port2):
        while True:
            connect = False
            while not connect:
                try:
                    install_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    install_socket.connect((ip2,port2))
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