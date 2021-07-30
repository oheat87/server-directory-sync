

"""
    SIMPLE INTERFACE
"""

import os
import re
import mainTest

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
    
    # restore()
    # synchronizationCheck()
    # runInBackground()
    
    # getSetting()
    # changeServers()
    # changeDirectoryPath()
    # changeTimeInterval()
    # runUnInstall
    
    [x] # clear()
    
"""

# INSTALL =================================================================
def runInstall():
    pos=" >> INSTALL \n"
    line="=============================="
    print(title,line,"\n",pos,line)
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
    port1=input(" > Port-1: ")
    ip2=input(" > IP-2: ")
    port2=input(" > Port-2: ")
    directory_path=input(" > DirectoryPath: ")
    sync_time_interval=input(" > SyncTimeInterval(s): ")


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

    try:
        check=f"[ERROR] Invalid Port-2: {port2}"
        int(port2)
    except:
        print(check)

    if not os.path.exists(directory_path):
        check=f"[ERROR] DirectoryPath {directory_path} not exist!"
        print(check)

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
            return port1,ip2,port2,directory_path,sync_time_interval
        else:
            unInstalled()
    else:
        RorN = input(" > Press 'R' to reset the input [R/n] ")
        clear()
        if RorN=='R' or RorN=='r':
            runInstall()
        else:
            unInstalled()


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
    if num=='0': mainTest.main()
    elif num=='1': restore()
    elif num=='2': pass
    elif num=='3': pass
    elif num=='4': pass
    elif num=='5': os._exit(0)
    else: installedWithProgramStopped()


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
        unInstalled()

#TODO
# RESTORE ==================================================================
def restore():
    clear()
    print("현재위치: ",os.getcwd())
    # demo_list = ['2021-07-21 13-46-54.918.zip', '2021-07-22 13-46-54.918.zip', '2021-07-23 13-46-54.918.zip']
    backup_list=os.listdir(os.getcwd())
    pos=" >> Restore \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    print("         [Backup List]        ")
    num=0
    for item in backup_list:
        print(f" <{num+1}>",item)
        num+=1

#TODO
# SYNCHRONIZATION CHECK ======================================================
def synchronizationCheck():
    pos=" >> Synchronization Check \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    srv1=" srv1: localhost"
    srv2="srv2: xxx.xxx.x.x"
    print(srv1,'\n',srv2)
    print("",line)
    #print(" Some files need to be synchronized.")
    #print(" Press 'Y' to run synchronization. [Y/n] ")

    print(" All have been synchronized.")
    print(" Press 'E' to exit. ")

#TODO
# RUN IN BACKGROUND ======================================================
def runInBackground():
    pos=" >> Run in background \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    print(" Interface will run in background.\n"
          " Press 'Y' to continue. [Y/n] ")

#TODO
# SETTING ================================================================
def getSetting():
    pos=" >> Change settings \n"
    line="=============================="
    print(title,line,"\n",pos,line)

    print(" [Servers] \n"
          "   IP-1: localhost\n"
          "   Port-1: 10\n"
          "   IP-2: xxx.xxx.x.x\n"
          "   Port-2: 20\n"
          " [DirectoryPath] /home/xxx\n"
          " [TimeInterval] 30 sec\n"
          " [ProgramStartedAt] 2021-07-23 13:02:29,123\n"
          " [InstalledAt] 2021-07-23 10:00:00,000")
    print(" [Uninstall] Enter 'uninstall' ")
    print(line)
    print("Select to change: ")

#TODO
# Change: SERVERS ================================================================
def changeServers():
    pos=" >> Change 'Servers' \n"
    line="=============================="
    print(title,line,"\n",pos,line)

    print(" [Servers] \n"
          "   IP-1: localhost\n"
          "   Port-1: 10\n"
          "   IP-2: xxx.xxx.x.x\n"
          "   Port-2: 20\n"
          " [DirectoryPath] /home/xxx")
    # get input line by line if no-change press 'Enter'
    print(line)
    print("<If no-change just press 'Enter'>")
    print(" > IP-1 change to:\n"
          " > Port-1 change to:\n"
          " > IP-2 change to:\n"
          " > Port-2 change to:\n"
          " > DiretoryPath change to:")

#TODO
# Change: DIRECTORY PATH ===========================================================
def changeDirectoryPath():
    pos=" >> Change 'DirectoryPath' \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    print(" [DirectoryPath] /home/xxx")
    print(line)
    print("<If no-change just press 'Enter'>")
    print(" > Change to: ")

#TODO
# Change: TimeInterval ======================================================
def changeTimeInterval():
    pos=" >> Change 'TimeInterval' \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    print(" [TimeInterval] 30 sec")
    print(line)
    print("<If no-change just press 'Enter'>")
    print(" > Change to: ")

#TODO
# Change: Uninstall =========================================================
def runUnInstall():
    pos=" >> UNINSTALL \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    print(" Remove all data in syncPro and \n"
          " UNINSTALL the program? \n"
          " [Y/N]")

# clear =====================================================================
def clear():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

