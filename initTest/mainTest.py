"""
    update: 2021/07/16

    store logs to the [date].json file (동기화 프로그램의 과정을 로그파일로 저장)

    구현내용:
    1. store logs of create or delete files in [date].json (파일 생성, 삭제에대한 동기화 로그 저장)
        +5. add 'modified' flag
    2. merge code with rttTest.py (코드 merge)
    3. change the install path & get the arguments from setting file (설치위치 수정, 설치 후 값을 setting파일에서 읽어오기)
    4. setting.json: 'latestsync'->'installTime', add & update 'startedTime'

"""


import sys

#modules for socket communication
import socket
import threading
import time

#modules for file system tracking
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import PatternMatchingEventHandler

#import user module
import newTmpTest
import syncJobTest
import rttTest
import recursiveTracker

#install & init_setting
import initTest
import json
import datetime
import _install
import backupTest
import _interface
import keyboard

#some constants
MAX_LISTEN = 100
MAX_BUFFER_LEN= 1024
# IP_ADDR = '192.168.2.60'
# IP_ADDR = '127.0.0.1'
DEFAULT_TIME_INTERVAL = 30
SERVER_MIN_WAIT_TIME=3 # for waiting message of exchage file function, minimum waiting time
MIN_DIFF_TIME=10 # for waiting message of exchage file function, minimum difference btw MIN_WAIT_TIME and time interval
SERVER_WAIT_TIME_MULTIPLE=5 # for waiting message of exchage file function, number multiplied to half_avg_rtt

#debug constants
# DEBUG_PORT=3500
# DEBUG_IP_ADDR='127.0.0.1'
# DEBUG_PATH='C:\\Users\\한태호\\Documents\\pyRepos\\dsTest\\testFolder'

def getServerWaitTime(avg_rtt,time_interval=DEFAULT_TIME_INTERVAL):
    time_candidate1=(avg_rtt/2)*SERVER_WAIT_TIME_MULTIPLE
    time_candidate2= time_interval-MIN_DIFF_TIME
    #check if server's minimum wait time is less than (time interval)-(MIN_DIFF_TIME)
    if SERVER_MIN_WAIT_TIME>time_candidate2:
        print('[dsTest getSWT] illegal wait time setting!')
        sys.exit(1)
    if time_candidate1<1:
        return SERVER_MIN_WAIT_TIME
    else:
        return min(time_candidate1,time_candidate2)

#simple data structure
class fsTracker():
    def __init__(self):
        self.dictionary={}
        self.start_time=time.time()
        pass
    def pushEvent(self,file_name,flag,time_stamp):
        if file_name not in self.dictionary:
            self.dictionary[file_name]=[flag,time_stamp-self.start_time]
            return
        event_content=self.dictionary[file_name]
        if event_content[0]=='m':
            if flag=='m':
                event_content[1]=time_stamp-self.start_time
            elif flag=='d':
                event_content[0]=flag
                event_content[1]=time_stamp-self.start_time
            else:
                print('[fsTracker.pushEvent] invalid file operation sequence occured')
                return
        elif event_content[0]=='c':
            if flag=='m':
                event_content[1]=time_stamp-self.start_time
            elif flag=='d':
                del self.dictionary[file_name]
            else:
                print('[fsTracker.pushEvent] invalid file operation sequence occured')
                return
        elif event_content[0]=='d':
            if flag=='c':
                event_content[0]='m'
                event_content[1]=time_stamp-self.start_time
            else:
                print('[fsTracker.pushEvent] invalid file operation sequence occured')
                return

    def checkTracked(self,fname):
        return fname in self.dictionary

    def getContent(self):
        return self.dictionary
    def delContent(self):
        del self.dictionary
    def resetContent(self):
        del self.dictionary
        self.dictionary={}
    
    def printContent(self):
        print('----------------------dataStructure Content--------------------')
        for file_name in self.dictionary:
            print(file_name,end=' ')
            print(self.dictionary[file_name][0],end=' ')
            print(self.dictionary[file_name][1])
        print('-------------------------------------------------------------------')


class Handler(FileSystemEventHandler):
    def __init__(self, dir_root_path):
        self.fs_tracker=recursiveTracker.fsTracker(dir_root_path,time.time())

    def typeNameExtension(self, event):
        # function for get a full string that expresses what happened to folder
        return_str = f'event type: {event.event_type}, '
        fname, ext = os.path.splitext(os.path.basename(event.src_path))
        return_str += f'filename: {fname}, extension: {ext}'
        return return_str
    def on_created(self,event):
        self.fs_tracker.on_created(event)
    def on_deleted(self,event):
        self.fs_tracker.on_deleted(event)
    def on_modified(self,event):
        self.fs_tracker.on_modified(event)
    def on_moved(self,event):
        self.fs_tracker.on_moved(event)
    # function for getting tracker instance being used
    def getTracker(self):
        return self.fs_tracker

    # function for clear memory of dictionary instance
    def delTracker(self):
        self.fs_tracker.delContent()
        
#class for watching a folder
class Watcher:
    def __init__(self,path,end_time):
        
        self.event_handler = Handler(path)
        self.observer = Observer()
        self.target_dir= path
        self.end_time=end_time
        os.chdir(path)
        print(f'[filesystem watcher] now watching {os.getcwd()}')

    def currentDirectorySetting(self):
        #function for change current working directory
        os.chdir(self.target_dir)
        print('[filesystem watcher] first directory setting....')
        print(f'[filesystem watcher] cwd: {os.getcwd()}')

    def run(self):
        #function for running filesystem watcher
        self.observer.schedule(self.event_handler,self.target_dir,recursive=True)
        self.observer.start()
        #keep watching a folder until run out of time or get keyboard interrupt
        # start_time=time.time()
        try:
            while True:
                cur_time=time.time()
                if time.time()>=self.end_time:
                    self.observer.stop()
                    return True
                time.sleep(0.1)
                if keyboard.is_pressed('1'):
                    self.observer.stop()
                    _interface.clear()
                    print("<<<<<<<<<<<<STOP THE PROGRAM!>>>>>>>>>>>>>>")
                    return False
                elif keyboard.is_pressed('2'):
                    _interface.clear()
                    print("<<<<exit>>>>")
                    os._exit(0)

        except KeyboardInterrupt as e:
            print('[filesystem watcher] exiting program...')
            print('[filesystem watcher] shutting down program given keyboard interrupt')
            self.observer.stop()
            return False

    # function for getting tracker instance being used by event handler
    def getTracker(self):
        return self.event_handler.getTracker()
    # function for clear memory of dictionary instance
    def delTracker(self):
        self.event_handler.delTracker()


def mainPro():
    # check system arguments num
    ##    if len(sys.argv)!=4:
    ##        print('wrong system arguments!')
    ##        sys.exit(1)
    # ---------- save cwd & pass target path to backupTest module
    # print('[main thread] saving paths')

    # backupTest.setPaths(os.getcwd(),sys.argv[3])

    archive_path = os.getcwd()
    _interface.PROG_PATH=archive_path
    _interface.BACKUP_PATH=os.path.join(archive_path, 'syncPro', 'backup')
    install_path = os.path.join(os.getcwd(), "syncPro")
    if os.path.exists(os.path.join(install_path, "setting.json")):
        with open(os.path.join(install_path, "setting.json"), 'r') as f:
            setting = json.load(f)
        _interface.TARGET_PATH=setting["dirPath"]
        ### UNINSTALL ###
        if setting["install"] == False:
            print("=============unInstall start=================")
            if setting["installTime"] != "":
                _install.unInstall(install_path, setting["dirPath"])
        #################

        # ---------- time synchronization process
        print('[main thread] doing time synchronization')
        prev_endtime,avg_rtt = rttTest.waitToSync(setting["servers"][1]["ip_2"], setting["servers"][0]["port_1"],
                                          int(setting["servers"][1]["port_2"]))
        print('[main thread] time synchronization done')

        # re-start the program
        log_path = initTest.main(int(setting["servers"][0]["port_1"]), setting["servers"][1]["ip_2"],int(setting["servers"][1]["port_2"]),
                                 setting["dirPath"], setting["timeInterval"])

    ### install start ==========================================
    if not os.path.exists(install_path):
        # get input from user interface
        port1, \
        ip2, \
        port2, \
        directory_path, \
        sync_time_interval \
            = _interface.unInstalled()
        _interface.TARGET_PATH=directory_path
        prev_endtime, avg_rtt = rttTest.waitToSync(ip2, int(port1), int(port2))

        log_path = initTest.main(port1, ip2, port2, directory_path, sync_time_interval)

    with open(os.path.join(install_path, "setting.json"), 'r') as f:
        setting = json.load(f)
    # update started time
    setting["startedTime"] = str(datetime.datetime.now()).replace(":", "-")[:-3]
    with open(os.path.join(install_path, "setting.json"), 'w', encoding='utf-8') as mk:
        json.dump(setting, mk, indent='\t')

    _interface.installedWithProgramRunning()

    ### install end ============================================

    # ---------- make filesystem watcher and do synchronization process on every time interval
    while True:
        backupTest.setPaths(archive_path, setting["dirPath"])

        # do directory backup
        print('[main thread] doing directory backup')
        backupTest.backupDir(backupTest.ARCHIVE_PATH, backupTest.TARGET_PATH)
        print('[main thread] directory backup done')

        prev_endtime += int(setting["timeInterval"])
        watcher = Watcher(setting["dirPath"], prev_endtime)
        do_synchronization = watcher.run()
        if not do_synchronization:
            break

        # DEBUG
        print('[main thread] sync process on time interval activated!')

        # send track data
        ds = watcher.getTracker()
        my_trackData=ds.getContent()
        print(my_trackData)
        JSON_fname = newTmpTest.makeJSON(my_trackData)
        print('JSON file', JSON_fname, 'successfully created')

        # receive&load track data
        received_fname = newTmpTest.exchangeTrackData(JSON_fname, setting["servers"][1]["ip_2"],
                                                      int(setting["servers"][0]["port_1"]),
                                                      int(setting["servers"][1]["port_2"]))
        received_trackData = newTmpTest.loadJSON(received_fname)

        # delete temporary JSON files
        os.remove(JSON_fname)
        os.remove(received_fname)

        ##        # DEBUG: print received track data
        ##        tds= fsTracker()
        ##        tds.dictionary= received_trackData
        ##        print('------------------received Track Data--------------------')
        ##        tds.printContent()

        # sync target directory structure
        recursiveTracker.syncDirectories(setting["dirPath"],my_trackData,received_trackData)

        # get file lists of being deleted, sent and received        
##        deleteList,sendList,my_modifiedList=syncJobTest.getJobList(ds.getContent(),received_trackData)
##        deleteList, sendList, recv_createList, recv_modifiedList = syncJobTest.getJobList(ds.getContent(),
##                                                                                          received_trackData)
        dList,sList,rList=recursiveTracker.getJobList(setting["dirPath"],my_trackData,received_trackData)

        # here, need to delete dictionaries!!!!
        ds.delContent()
        del received_trackData

        # DEBUG
        print('------------delete List----------------')
        for fname in dList: print(fname)
        print('------------send List----------------')
        for fname in sList: print(fname)
        print('------------receive List----------------')
        for fname in rList: print(fname)

        # first, delete files to synchronize
        # we can do some file backup operations here before really delete the file
        # use deleteList
        pass
        # do deletions
        syncJobTest.deleteFiles(dList)

        # second, send newly created and modified files to other side
        # we can do some file backup operations here before really overwrite the file
        # use my_modifiedList
        pass
        # do file exchange and overwrite via socket communication
        syncJobTest.exchangeFiles(sList, setting["servers"][1]["ip_2"], int(setting["servers"][0]["port_1"]),
                                  int(setting["servers"][1]["port_2"]),setting["dirPath"],getServerWaitTime(avg_rtt))

        # clean instance memory
        del watcher

        # DEBUG
        print('[main thread] sync process on time interval done')

    _interface.installedWithProgramStopped()

    print('[main thread] end entire program')


if __name__ == '__main__':
    mainPro()
