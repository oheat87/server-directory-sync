import os
import json
import _logtojson

def create(path):
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

