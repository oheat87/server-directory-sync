

"""
    SIMPLE INTERFACE
"""

import os
import re
import mainTest
import backupTest
import json
import _install

title="\
█▀▀ █  █ █▀▀▄ █▀▀ █▀▀█ █▀▀█ █▀▀█ \n\
▀▀█ █▄▄█ █  █ █   █▄▄█ █▄▄▀ █  █ \n\
▀▀▀ ▄▄▄█ ▀  ▀ ▀▀▀ █    ▀ ▀▀ ▀▀▀▀ \n"

# FOR IP ADDR CHECK
regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"

""" 
     Functions TODO List
===============================
    [x] # runInstall()
            ## TODO ##
            => get setting values from setting.json file (format: /unused/setting.json)
            => get setting values from user input 
    [x] # installedWithProgramStopped()
    [x] # installedWithProgramRunning()
    [x] # unInstalled()
    
    [x] # restore()
    ===TODO # synchronizationCheck() 
    ===TODO # runInBackground() 
    
    [x] # getSetting()
    [x] # changeServers()
    [x] # changeDirectoryPath()
    [x] # changeTimeInterval()
    [x] # runUnInstall
    
    [x] # clear()
    
"""
PROG_PATH=""
TARGET_PATH=""
BACKUP_PATH=""

# INSTALL =================================================================
def runInstall():
    pos = " >> INSTALL \n"
    line = "=============================="
    print(title, line, "\n", pos, line)
    print(" <Init Setting>")
    # print(" > IP-1: \n"
    #       " > Port-1: \n"
    #       " > IP-2: \n"
    #       " > Port-2: \n"
    #       " > DirectoryPath: \n"
    #       " > SyncTimeInterval: \n"
    #       " Press 'Y' to install [Y/n]")
    # ip1=input(" > IP-1: localhost")
    print(" > IP-1: localhost")
    port1 = input(" > Port-1: ")
    ip2 = input(" > IP-2: ")
    port2 = input(" > Port-2: ")
    directory_path = input(" > DirectoryPath: ")
    sync_time_interval = input(" > SyncTimeInterval(s): ")

    # check invalid input =======================================================
    check=""
    try:
        check=f"[ERROR] Invalid Port-1: {port1}"
        int(port1)
    except:
        print(check)

    # check IP ADDR
    if (re.search(regex, ip2)): pass
    else:
        check=f"[ERROR] Invalid Ip address: {ip2}"
        print(check)
        RorN = input(" > Press 'R' to reset the input [R/n] ")
        clear()
        if RorN == 'R' or RorN == 'r':
            return runInstall()
        else:
            return unInstalled()

    try:
        check=f"[ERROR] Invalid Port-2: {port2}"
        int(port2)
    except:
        print(check)

    if not os.path.exists(directory_path):
        check=f"[ERROR] DirectoryPath {directory_path} not exist!"
        print(check)
    else:
        try:
            check=f"[ERROR] Invalid SyncTimeInterval(s): {sync_time_interval}"
            int(sync_time_interval)
            check="" #reset
        except:
            print(check)
    # invalid check end =======================================================================

    if check=="": # PASS
        YorN=input(" Press 'Y' to install [Y/n] ")
        clear()
        if YorN=='Y' or YorN=='y':
            # os._exit(0)
            # print(port1,ip2,port2,directory_path,sync_time_interval)
            return port1,ip2,port2,directory_path,sync_time_interval
        else:
            return unInstalled()
    else:
        RorN = input(" > Press 'R' to reset the input [R/n] ")
        clear()
        if RorN=='R' or RorN=='r':
            return runInstall()
        else:
            return unInstalled()


# INSTALLED, PROGRAM STOPPED ===============================================
def installedWithProgramStopped():
    clear()
    install_status=" [install status] installed \n"
    program_status=" [program status] stopped\n"
    line="==============================\n"

    menu="<0> Re-start program\n" \
         " <1> Restore \n" \
         " <2> Synchronization check \n" \
         " <3> Run in background \n" \
         " <4> Setting \n" \
         " <5> Exit \n"

    print(title,line,install_status,program_status,line,menu)

    num=input("Enter the number: ")
    if num=='0': return mainTest.mainPro()
    elif num=='1': return restore()
    elif num=='2': return synchronizationCheck()
    elif num=='3': return runInBackground()
    elif num=='4': return getSetting()
    elif num=='5': os._exit(0)
    else: return installedWithProgramStopped()


# INSTALLED, PROGRAM RUNNING ===============================================
def installedWithProgramRunning():
    clear()
    install_status=" [install status] installed \n"
    program_status=" [program status] running\n"
    line="==============================\n"

    menu="<1> Stop the program \n" \
         "     (MAIN MENU)\n" \
         " <2> Exit \n"

    print(title,line,install_status,program_status,line,menu)


# UNINSTALLED ==============================================================
def unInstalled():

    install_status=" [install status] unInstalled \n"
    # program_status=" [program status] stopped\n"
    line="==============================\n"

    menu="<1> Install \n" \
         " <2> Exit \n"

    print(title,line,install_status,line,menu)
    # choose menu num
    num=input("Enter the number: ")
    clear()
    if num=='1':
        return runInstall()
    elif num=='2':
        os._exit(0)
    else:
        return unInstalled()


# RESTORE ==================================================================
def restore():
    clear()
    # print("현재위치: ",BACKUP_PATH)
    # demo_list = ['2021-07-21 13-46-54.918.zip', '2021-07-22 13-46-54.918.zip', '2021-07-23 13-46-54.918.zip']
    backup_list=os.listdir(BACKUP_PATH)
    pos=" >> Restore \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    print("         [Backup List]        ")
    num=0
    for item in backup_list:
        print(f" <{num+1}>",item)
        num+=1
    try:
        zip_num=input("Enter the number to restore (E-exit): ")
        if zip_num=='E' or zip_num=='e':
            return installedWithProgramStopped()
        if int(zip_num)<=0 or int(zip_num)>len(backup_list):
            return restore()
    except:
        return restore()

    zip_name=backup_list[int(zip_num)-1]
    backupTest.restoreDir(BACKUP_PATH,TARGET_PATH,zip_name)
    # print("되돌리기 완료")
    return restore()


# SETTING ================================================================
def getSetting():
    clear()
    pos=" >> Change settings \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    # print(os.path.join(PROG_PATH,"syncPro", "setting.json"))
    with open(os.path.join(PROG_PATH,"syncPro", "setting.json"), 'r') as f:
        setting = json.load(f)

    print(" [Servers] \n"
          "   IP-1: localhost\n"
          f"   Port-1: {setting['servers'][0]['port_1']}\n"
          f"   IP-2: {setting['servers'][1]['ip_2']}\n"
          f"   Port-2: {setting['servers'][1]['port_2']}\n"
          f" [DirectoryPath] {setting['dirPath']}\n"
          f" [TimeInterval] {setting['timeInterval']} sec\n"
          f" [ProgramStartedAt] {setting['startedTime']}\n"
          f" [InstalledAt] {setting['installTime']}")
    print(" - [Uninstall] Enter 'uninstall' ")
    print(" - Enter 'R' to return to Main Menu ")
    print(line)
    print("You can change [Servers], [DirectoryPath], [TimeInterval] and run [Uninstall]")
    str=input("Select to change: ")
    if str.lower()=='servers' or str.lower()=='server':
        return changeServers()
    elif str.lower()=='directorypath' or str.lower()=='dirpath':
        return changeDirectoryPath()
    elif str.lower()=='timeinterval':
        return changeTimeInterval()
    elif str.lower()=='uninstall':
        return runUnInstall()
    elif str=='R':
        return installedWithProgramStopped()
    else:
        return getSetting()



# Change: SERVERS ================================================================
def changeServers():
    clear()
    pos=" >> Change 'Servers' \n"
    line="=============================="
    print(title,line,"\n",pos,line)

    ################
    setFile = os.path.join(PROG_PATH, "syncPro", "setting.json")
    with open(setFile, 'r') as f:
        setting = json.load(f)
    ################

    print(" [Servers] \n"
          "   IP-1: localhost\n"
          f"   Port-1: {setting['servers'][0]['port_1']}\n"
          f"   IP-2: {setting['servers'][1]['ip_2']}\n"
          f"   Port-2: {setting['servers'][1]['port_2']}\n"
          f" [DirectoryPath] {setting['dirPath']}")

    # get input line by line if no-change press 'Enter'
    print(line)
    print("<If no-change just press 'Enter'>")
    # print(" > IP-1 change to:\n"
    #       " > Port-1 change to:\n"
    #       " > IP-2 change to:\n"
    #       " > Port-2 change to:\n"
    #       " > DiretoryPath change to:")
    print(" > IP-1: localhost")
    port1 = input(" > Port-1: ")
    ip2 = input(" > IP-2: ")
    port2 = input(" > Port-2: ")
    directory_path = input(" > DirectoryPath: ")

    # check invalid input =======================================================
    check=""
    try:
        check=f"[ERROR] Invalid Port-1: {port1}"
        if port1=="":
            pass
        else:
            int(port1)
            setting['servers'][0]['port_1']=port1
    except:
        print(check)

    # check IP ADDR
    if ip2=="":
        pass
    else:
        if (re.search(regex, ip2)):
            setting['servers'][1]['ip_2']=ip2
        else:
            check=f"[ERROR] Invalid Ip address: {ip2}"
            print(check)

    try:
        check=f"[ERROR] Invalid Port-2: {port2}"
        if port2=="":
            pass
        else:
            int(port2)
            setting['servers'][1]['port_2'] = port2
    except:
        print(check)

    if directory_path=="":
        pass
    else:
        if not os.path.exists(directory_path):
            check=f"[ERROR] DirectoryPath {directory_path} not exist!"
            print(check)
        else:
            setting['dirPath']=directory_path
            check==""
    # invalid check end =======================================================================

    if check=="": # PASS
        with open(setFile, 'w', encoding='utf-8') as mk:
            json.dump(setting, mk, indent='\t')
        return getSetting()
    else:
        RorN = input(" > Press 'R' to reset the input [R/n] ")
        clear()
        if RorN=='R' or RorN=='r':
            return changeServers()
        else:
            return getSetting()




# Change: DIRECTORY PATH ===========================================================
def changeDirectoryPath():
    clear()
    pos=" >> Change 'DirectoryPath' \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    ################
    setFile = os.path.join(PROG_PATH, "syncPro", "setting.json")
    with open(setFile, 'r') as f:
        setting = json.load(f)
    ################
    print(f" [DirectoryPath] {setting['dirPath']}")
    print(line)
    print("<If no-change just press 'Enter'>")
    path=input(" > Change to: ")
    if path=="":
        return getSetting()
    else:
        if os.path.exists(path):
            setting['dirPath']=path
            with open(setFile, 'w', encoding='utf-8') as mk:
                json.dump(setting, mk, indent='\t')
            return getSetting()
        else:
            return changeDirectoryPath()



# Change: TimeInterval ======================================================
def changeTimeInterval():
    clear()
    pos=" >> Change 'TimeInterval' \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    ################
    setFile = os.path.join(PROG_PATH, "syncPro", "setting.json")
    with open(setFile, 'r') as f:
        setting = json.load(f)
    ################
    print(f" [TimeInterval] {setting['timeInterval']} sec")
    print(line)
    print("<If no-change just press 'Enter'>")
    timeInt=input(" > Change to: ")
    if timeInt=="":
        return getSetting()
    else:
        try:
            int(timeInt)
            setting['timeInterval']=timeInt
            with open(setFile, 'w', encoding='utf-8') as mk:
                json.dump(setting, mk, indent='\t')
        except:
            print("[Error] Wrong input")
    return changeTimeInterval()


# Change: Uninstall =========================================================
def runUnInstall():
    clear()
    pos=" >> UNINSTALL \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    YorN=input(" Remove all data in syncPro and \n"
          " UNINSTALL the program? \n"
          " [Y/N]")
    if YorN=='Y' or YorN=='y':
        ################
        setFile = os.path.join(PROG_PATH,"syncPro", "setting.json")
        with open(setFile, 'r') as f:
            setting = json.load(f)
        print(setting['install'])
        setting["install"]=False

        with open(setFile, 'w', encoding='utf-8') as mk:
            json.dump(setting, mk, indent='\t')
        ################
        return _install.unInstall(os.path.join(PROG_PATH,"syncPro"), TARGET_PATH)
    elif YorN=='N' or YorN=='n':
        return getSetting()
    else:
        return runUnInstall()


# clear =====================================================================
def clear():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)



# ====================================================================================
# ====================================================================================
# ====================================================================================


# TODO
# SYNCHRONIZATION CHECK ==============================================================
def synchronizationCheck():
    clear()
    pos=" >> Synchronization Check \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    ################
    setFile = os.path.join(PROG_PATH, "syncPro", "setting.json")
    with open(setFile, 'r') as f:
        setting = json.load(f)
    ################
    srv1=" srv1: localhost"
    srv2=f"srv2: {setting['servers'][1]['ip_2']}"
    print(srv1,'\n',srv2)
    print("",line)
    #print(" Some files need to be synchronized.")
    #print(" Press 'Y' to run synchronization. [Y/n] ")

    # print(" All have been synchronized.")
    # print(" Press 'E' to exit. ")
    print("NEED TO BE DEVELOPED.")
    input()
    return installedWithProgramStopped()

# TODO
# RUN IN BACKGROUND ==================================================================
def runInBackground():
    clear()
    pos=" >> Run in background \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    # print(" Interface will run in background.\n"
    #       " Press 'Y' to continue. [Y/n] ")
    print("NEED TO BE DEVELOPED.")
    input()
    return installedWithProgramStopped()