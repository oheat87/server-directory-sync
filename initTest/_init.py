import os

def create(path):
    try:
        if os.path.isdir(path):
            install_path=path+'\\syncPro'
            os.makedirs(install_path)
            os.makedirs(install_path+'\\backup')
            os.makedirs(install_path+'\\log')
            f=open(install_path+'\\setting.json','w')
            f.close()
    except OSError:
        print('Error: Creating directory. ' + path)