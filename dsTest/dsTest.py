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

#some constants
MAX_LISTEN = 100
MAX_BUFFER_LEN= 1024
##IP_ADDR = '192.168.2.53'
IP_ADDR = '127.0.0.1'
DEFAULT_TIME_INTERVAL=120

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

#class for server threading
class server_thread(threading.Thread):
    def __init__(self,name, socket):
        super().__init__()
        self.name = name
        self.server_socket=  socket
        self.connection_socket=None

    def run(self):
        # run server thread by listening to server listening socket and
        # by responding to connection socket
        print('[server thread] start ', threading.currentThread().getName())
        try:
            while True:
                self.connection_socket,addr = self.server_socket.accept()
                print('[server thread] access from',str(addr),'accepted')

                data = self.connection_socket.recv(MAX_BUFFER_LEN)
                msg= data.decode('utf-8')
                print('[server thread] another server file modification:',msg)

                self.connection_socket.close()
                self.connection_socket=None
        except socket.error as e:
            print('[server thread] socket error debug:',e)
            print('[server thread] exiting....')

        # before finishing, close all the sockets this server thread has
        self.closeAllSocket()
        print('[server thread] end ', threading.currentThread().getName())
    def stop(self):
        # stop server thread by closing all the sockets that this thread has
        self.closeAllSocket()
    def closeAllSocket(self):
        # method for close all sockets that this server thread has
        # first, close server listening socket
        try:
            if self.server_socket.fileno()>=0:
                self.server_socket.close()
                print('[server thread] server socket closed')
        except socket.error as e:
            print('[server thread] server socket has already been closed')
            print('[server thread] exception content:',e)
        # second, close server connection socket
        try:
            if self.connection_socket is not None and self.connection_socket.fileno()>=0:
                self.connection_socket.close()
                print('[server thread] server connection socket closed')
        except socket.error as e:
            print('[server thread] connection socket has already been closed')
            print('[server thread] exception content:',e)

# class for defining file system event handler
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
    def __init__(self,path,time_interval):
        
        self.event_handler = Handler()
        self.observer = Observer()
        self.target_dir= path
        self.time_interval=time_interval
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
        start_time=time.time()
        try:
            while True:
                cur_time=time.time()
                if cur_time-start_time>=self.time_interval:
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

    #---------- make filesystem watcher and do synchronization process on every time interval
    while True:
        watcher= Watcher(sys.argv[3],DEFAULT_TIME_INTERVAL)
        do_synchronization= watcher.run()
        if not do_synchronization:
            break

        #DEBUG
        print('[main thread] sync process on time interval activated!')

        # send track data
        ds=watcher.getTracker()
        JSON_fname=newTmpTest.makeJSON(ds.getContent())
        print('JSON file',JSON_fname,'successfully created')

        # receive&load track data
        received_fname= newTmpTest.exchangeTrackData(JSON_fname,IP_ADDR,int(sys.argv[1]),int(sys.argv[2]))
        received_trackData= newTmpTest.loadJSON(received_fname)

        # delete temporary JSON files
        os.remove(JSON_fname)
        os.remove(received_fname)
        
##        # DEBUG: print received track data
##        tds= fsTracker()
##        tds.dictionary= received_trackData
##        print('------------------received Track Data--------------------')
##        tds.printContent()
        
        deleteList,sendList,my_modifiedList=syncJobTest.getJobList(ds.getContent(),received_trackData)
        # here, need to delete dictionaries!!!!
        ds.resetContent()
        del received_trackData
        
        
        #DEBUG
        print('------------delete List----------------')
        for fname in deleteList: print(fname)
        print('------------send List----------------')
        for fname in sendList: print(fname)
        print('------------modified List----------------')
        for fname in my_modifiedList: print(fname)
        
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
        syncJobTest.exchangeFiles(sendList,IP_ADDR,int(sys.argv[1]),int(sys.argv[2]))

        # clean instance memory
        del watcher

        #DEBUG
        print('[main thread] sync process on time interval done')
    
    print('[main thread] end entire program')
