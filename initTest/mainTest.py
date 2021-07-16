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

#install & init_setting
import initTest
import json
import datetime

#some constants
MAX_LISTEN = 100
MAX_BUFFER_LEN= 1024
IP_ADDR = '192.168.2.60'
# IP_ADDR = '127.0.0.1'
DEFAULT_TIME_INTERVAL=30

#debug constants
DEBUG_PORT=3500
DEBUG_IP_ADDR='127.0.0.1'
DEBUG_PATH='C:\\Users\\한태호\\Documents\\pyRepos\\dsTest\\testFolder'

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
    def __init__(self):
        self.tracker= fsTracker()
        pass
    def typeNameExtension(self,event):
        # function for get a full string that expresses what happened to folder
        return_str=f'event type: {event.event_type}, '
        fname,ext=os.path.splitext(os.path.basename(event.src_path))
        return_str+=f'filename: {fname}, extension: {ext}'
        return return_str
    def on_created(self,event):
        self.tracker.pushEvent(os.path.basename(event.src_path),'c',time.time())
    def on_deleted(self,event):
        self.tracker.pushEvent(os.path.basename(event.src_path),'d',time.time())
    def on_modified(self,event):
        self.tracker.pushEvent(os.path.basename(event.src_path),'m',time.time())
    def on_moved(self,event):
        self.tracker.pushEvent(os.path.basename(event.src_path),'d',time.time())
        self.tracker.pushEvent(os.path.basename(event.dest_path),'c',time.time())

    # function for getting tracker instance being used
    def getTracker(self):
        return self.tracker
    # function for clear memory of dictionary instance
    def delTracker(self):
        self.tracker.delContent()
        
#class for watching a folder
class Watcher:
    def __init__(self,path,end_time):
        
        self.event_handler = Handler()
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
        self.observer.schedule(self.event_handler,self.target_dir,recursive=False)
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


if __name__ == '__main__':
    # check system arguments num
##    if len(sys.argv)!=4:
##        print('wrong system arguments!')
##        sys.exit(1)
    install_path=os.getcwd()+"\\syncPro"
    if os.path.exists(install_path+"\\setting.json"):
        with open(install_path+"\\setting.json",'r') as f:
            setting = json.load(f)
        #---------- time synchronization process
        print('[main thread] doing time synchronization')
        prev_endtime=rttTest.waitToSync(IP_ADDR,int(setting["servers"][0]["port_1"]),int(setting["servers"][1]["port_2"]))
        print('[main thread] time synchronization done')

        # re-start the program
        log_path = initTest.main(int(setting["servers"][0]["port_1"]),int(setting["servers"][1]["port_2"]),setting["dirPath"],DEFAULT_TIME_INTERVAL)



    ### install start ==========================================
    if not os.path.exists(install_path):
        prev_endtime=rttTest.waitToSync(IP_ADDR,int(sys.argv[1]),int(sys.argv[2]))
        log_path = initTest.main(sys.argv[1],sys.argv[2],sys.argv[3],DEFAULT_TIME_INTERVAL)

    with open(install_path+"\\setting.json",'r') as f:
        setting = json.load(f)
    # update started time
    setting["startedTime"]=str(datetime.datetime.now()).replace(":", "-")[:-3]
    with open(install_path+"\\setting.json", 'w', encoding='utf-8') as mk:
        json.dump(setting, mk, indent='\t')
    # log 저장 위치를 return 받음
    ### install end ============================================



    #---------- make filesystem watcher and do synchronization process on every time interval
    while True:
        prev_endtime+=DEFAULT_TIME_INTERVAL
        watcher = Watcher(setting["dirPath"],prev_endtime)
        do_synchronization = watcher.run()
        if not do_synchronization:
            break

        #DEBUG
        print('[main thread] sync process on time interval activated!')

        # send track data
        ds=watcher.getTracker()
        print(ds.getContent())
        JSON_fname=newTmpTest.makeJSON(ds.getContent())
        print('JSON file',JSON_fname,'successfully created')

        # receive&load track data
        received_fname= newTmpTest.exchangeTrackData(JSON_fname,IP_ADDR,int(setting["servers"][0]["port_1"]),int(setting["servers"][1]["port_2"]))
        received_trackData= newTmpTest.loadJSON(received_fname)

        # delete temporary JSON files
        os.remove(JSON_fname)
        os.remove(received_fname)
        
##        # DEBUG: print received track data
##        tds= fsTracker()
##        tds.dictionary= received_trackData
##        print('------------------received Track Data--------------------')
##        tds.printContent()
        
        # deleteList,sendList,my_modifiedList=syncJobTest.getJobList(ds.getContent(),received_trackData)
        deleteList,sendList,recv_createList,recv_modifiedList=syncJobTest.getJobList(ds.getContent(),received_trackData)

        # here, need to delete dictionaries!!!!
        ds.resetContent()
        del received_trackData
        
        
        #DEBUG
        print('------------delete List----------------')
        for fname in deleteList: print(fname)
        print('------------send List----------------')
        for fname in sendList: print(fname)
        # print('------------modified List----------------')
        # for fname in my_modifiedList: print(fname)
        print('------------create List----------------')
        for fname in recv_createList: print(fname)
        print('------------modified List----------------')
        for fname in recv_modifiedList: print(fname)
        
        #first, delete files to synchronize
        #we can do some file backup operations here before really delete the file
        #use deleteList
        pass
        #do deletions
        syncJobTest.deleteFiles(deleteList)

        #second, send newly created and modified files to other side
        #we can do some file backup operations here before really overwrite the file
        #use my_modifiedList
        pass
        #do file exchange and overwrite via socket communication
        syncJobTest.exchangeFiles(sendList,IP_ADDR,int(setting["servers"][0]["port_1"]),int(setting["servers"][1]["port_2"]))

        # clean instance memory
        del watcher

        #DEBUG
        print('[main thread] sync process on time interval done')
    
    print('[main thread] end entire program')
