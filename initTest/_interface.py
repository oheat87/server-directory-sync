

"""
    SIMPLE INTERFACE

"""

import os

title="\
█▀▀ █  █ █▀▀▄ █▀▀ █▀▀█ █▀▀█ █▀▀█ \n\
▀▀█ █▄▄█ █  █ █   █▄▄█ █▄▄▀ █  █ \n\
▀▀▀ ▄▄▄█ ▀  ▀ ▀▀▀ █    ▀ ▀▀ ▀▀▀▀ \n"

# INSTALL =================================================================
def runInstall():
    pos=" >> INSTALL \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    print(" <Init Setting>")
    print(" > IP-1: \n"
          " > Port-1: \n"
          " > IP-2: \n"
          " > Port-2: \n"
          " > DirectoryPath: \n"
          " > SyncTimeInterval: \n"
          " Press 'Y' to install [Y/n]")

# INSTALLED, PROGRAM STOPPED ===============================================
def installedWithProgramStopped():

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

# INSTALLED, PROGRAM RUNNING ===============================================
def installedWithProgramRunning():
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
    program_status=" [program status] stopped\n"
    line="==============================\n"

    menu="<1> Install \n" \
         " <2> Exit \n"

    print(title,line,install_status,line,menu)

# RESTORE ==================================================================
def restore():
    demo_list = ['2021-07-21 13-46-54.918.zip', '2021-07-22 13-46-54.918.zip', '2021-07-23 13-46-54.918.zip']
    pos=" >> Restore \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    print("         [Backup List]        ")
    num=0
    for item in demo_list:
        print(f" <{num+1}>",item)
        num+=1


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

# RUN IN BACKGROUND ======================================================
def runInBackground():
    pos=" >> Run in background \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    print(" Interface will run in background.\n"
          " Press 'Y' to continue. [Y/n] ")

# SETTING ================================================================
def setting():
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

# Change: DIRECTORY PATH ===========================================================
def changeDirectoryPath():
    pos=" >> Change 'DirectoryPath' \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    print(" [DirectoryPath] /home/xxx")
    print(line)
    print("<If no-change just press 'Enter'>")
    print(" > Change to: ")

# Change: TimeInterval ======================================================
def changeTimeInterval():
    pos=" >> Change 'TimeInterval' \n"
    line="=============================="
    print(title,line,"\n",pos,line)
    print(" [TimeInterval] 30 sec")
    print(line)
    print("<If no-change just press 'Enter'>")
    print(" > Change to: ")

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



runUnInstall()
print("\033[H\033[J")
