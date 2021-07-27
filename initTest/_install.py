import os
import socket
import json
import zipfile
import _logtojson
import sys
import shutil

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
    "startedTime": "",
	"installTime": "",
	"install": False
}, indent=4)

    try:
        if os.path.isdir(path):
            install_path=os.path.join(path,'syncPro')
            os.makedirs(install_path)
            os.makedirs(os.path.join(install_path,'backup'))
            os.makedirs(os.path.join(install_path,'log'))
            f=open(os.path.join(install_path,'setting.json'),'w')
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
        self.install_path=os.path.join(install_path,'syncPro')
        install_log, time = _logtojson.run('install')
        os.chdir(path)
        print(f'[Install] directory path: {os.getcwd()}')

    def initSet(self,ip2,port2,interval):
        setFile = os.path.join(self.install_path , 'setting.json')

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

            #install = Install(setting["dirPath"], setting["servers"][1]["ip_2"], int(setting["servers"][1]["port_2"]))
            self.install(ip2,port2)
            setting["startedTime"]=time
            setting["timeInterval"]=interval
            setting["install"] = True
            setting["installTime"]=time

            # update json seeting file
            with open(setFile, 'w', encoding='utf-8') as mk:
                json.dump(setting, mk, indent='\t')

            # json format
            # _logtojson.log2json()

            # Back Up
            self.backUp(time)

            print("[install status] success!")

    def install(self,ip2,port2):

        # 수정: 하위폴더가 존재할 시, 하위폴더 우선 동기화
        for (path, dir, files) in os.walk(self.target_dir):
            # SOCKET
            connect = False
            while not connect:
                try:
                    install_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    install_socket.connect((ip2, port2))
                    connect = True
                except ConnectionRefusedError:  # 서버 연결 열릴 때 까지 대기
                    continue

            print("os.walk:",path,dir,files)
            # PATH
            filepath=path.replace(self.target_dir,"/")
            install_socket.sendall(str(filepath).encode())
            recv=install_socket.recv(MAX_BUFFER_LEN).decode() # path received
            print("[install msg]",recv)
            filepath=filepath[1:]

            # DIR
            install_socket.sendall(str(dir).encode())
            recv=install_socket.recv(MAX_BUFFER_LEN) # dir list received
            print("[install msg]",recv)

            # FILE
            install_socket.sendall(str(files).encode())
            recv=install_socket.recv(MAX_BUFFER_LEN) # file list received
            print("[install msg]",recv)

            ####
            install_socket.sendall('request to get filenum'.encode())

            filenum=install_socket.recv(MAX_BUFFER_LEN).decode()
            filenum=int(filenum)
            print("filenums:",filenum)

            for i in range(filenum):
                file = install_socket.recv(MAX_BUFFER_LEN).decode()  # 파일이름 받아옴
                print(f"send file [{filepath}/{file}] to server")
                filepath=os.path.join(filepath,file)
                if not file:
                    break
                try:
                    with open(os.path.join(path,file), 'rb') as f:
                        while True:
                            data = f.read(MAX_BUFFER_LEN)
                            if not data:
                                break
                            install_socket.sendall(data)
                except OSError as e:
                    print('there is no such file:', e)
                except KeyboardInterrupt:
                    os._exit(0)
            install_socket.close()

    def backUp(self,time):
        filename=os.path.join("backup",time+'.zip')
        new_zip = zipfile.ZipFile(os.path.join(self.install_path,filename), 'w')

        backup_target = self.target_dir

        for folder, subfolders, files in os.walk(backup_target):
            for file in files:
                new_zip.write(os.path.join(folder, file),
                              os.path.relpath(os.path.join(folder, file), backup_target),
                              compress_type=zipfile.ZIP_DEFLATED)

        new_zip.close()



def unInstall(install_path,target_dir):
    #Recovery
    setFile = os.path.join(install_path , 'setting.json')

    with open(setFile, 'r') as f:
        setting = json.load(f)

    # remove all files in targetDir
    target_dir_list=os.listdir(target_dir)
    for filename in target_dir_list:
        if os.path.isfile(os.path.join(target_dir,filename)):
            os.remove(os.path.join(target_dir,filename))
    # success to remove all files in targetDir


    # run recovery
    install_time=setting["installTime"]
    filename = os.path.join("backup", install_time + '.zip')
    with zipfile.ZipFile(os.path.join(install_path,filename), 'r') as recov_zip:
        recov_zip.extractall(target_dir)


    # os.rmdir(self.install_path) # remove all
    print("=============unInstall Success!=================")

    # remove program folder
    shutil.rmtree(install_path)

    sys.exit(0)

