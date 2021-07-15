import sys
import os

#modules for socket communication
import socket
import threading
import time

#probablistic experiment
import random

#some constants
MAX_LISTEN = 100
MAX_BUFFER_LEN= 1024
IP_ADDR = '192.168.2.53'
##IP_ADDR = '127.0.0.1'

PING_DEFAULT_COUNT=4
PING_STR_REQUEST='RTT_REQUEST'
PING_STR_REPLY='RTT_REPLY'
##PING_STR_REPLY_1='RTT_REPLY_1'
##PING_STR_REPLY_2='RTT_REPLY_2'

WAIT_TIME_DEFAULT=10

#global variable
server_thread_finished=False
this_process_faster=False

#debug constants
DEBUG_PORT=3500
DEBUG_IP_ADDR='127.0.0.1'
DEBUG_PATH='C:\\Users\\한태호\\Documents\\pyRepos\\dsTest\\testFolder'

#class for server threading
class rtt_server_thread(threading.Thread):
    def __init__(self,name, socket, ping_count):
        super().__init__()
        self.name = name
        self.server_socket=  socket
        self.connection_socket=None
        self.ping_count=ping_count

    def run(self):
        global server_thread_finished
        # run server thread by listening to server listening socket and
        # by responding to connection socket
##        print('[rtt_server thread] start ', threading.currentThread().getName())

        #handshaking part
        #get predefined handshaking string and receive the number of files being received
        try:
            while True:
                if self.ping_count<=0:
                    break
                self.connection_socket,addr = self.server_socket.accept()

                # get handshaking message
                data = self.connection_socket.recv(MAX_BUFFER_LEN)
                msg = data.decode('utf-8')
                if msg!=PING_STR_REQUEST:
                    print(f'[rtt_server thread] received message: {msg}')
                    print(f'msg==PING_STR_REQUEST: {msg==PING_STR_REQUEST}')
                    self.connection_socket.close()
                    self.connection_socket=None
                    continue
                self.connection_socket.sendall(PING_STR_REPLY.encode('utf-8'))

                self.connection_socket.close()
                self.connection_socket=None

                self.ping_count-=1
        except Exception as e:
            print('[rtt_server thread] error occured while handshaking')
            print(e)
            sys.exit(1)
        # to check which process of server(computer) is faster
        server_thread_finished=True
##        print(f'[rtt_server thread] completed replying ping request')

        # before finishing, close all the sockets this server thread has
        self.closeAllSocket()
##        print('[rtt_server thread] end ', threading.currentThread().getName())
    def stop(self):
        # stop server thread by closing all the sockets that this thread has
        self.closeAllSocket()
    def closeAllSocket(self):
        # method for close all sockets that this server thread has
        # first, close server listening socket
        try:
            if self.server_socket.fileno()>=0:
                self.server_socket.close()
##                print('[files_server thread] server socket closed')
        except socket.error as e:
            pass
##            print('[files_server thread] server socket has already been closed')
##            print('[files_server thread] exception content:',e)
        # second, close server connection socket
        try:
            if self.connection_socket is not None and self.connection_socket.fileno()>=0:
                self.connection_socket.close()
##                print('[files_server thread] server connection socket closed')
        except socket.error as e:
            pass
##            print('[files_server thread] connection socket has already been closed')
##            print('[files_server thread] exception content:',e)

def measureRTT(ip_addr,my_port_num,other_port_num,ping_count=PING_DEFAULT_COUNT):
    global server_thread_finished, this_process_faster
##    print('[rttTest measureRTT] start measuring RTT!')
    #---------------server part
    server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', my_port_num))
    server_socket.listen(MAX_LISTEN)

    st= rtt_server_thread('ST',server_socket,ping_count)
    st.start()

    #---------------client part
    # send PING_DEFALUT COUNT num of ping messages and measure RTT
    rtt_arr=[]
    
    try:
        for i in range(ping_count):
            client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            while True:
                try:
                    client_socket.connect((ip_addr,other_port_num))
                except ConnectionRefusedError:
                    time.sleep(0.001)
                    continue
                break
            
            start_time=time.time()
            client_socket.sendall(PING_STR_REQUEST.encode('utf-8'))
            client_socket.recv(MAX_BUFFER_LEN)
            end_time=time.time()
            print(f'[rttTest measureRTT] #{i+1} IP:{ip_addr}, RTT:{end_time-start_time}')
            rtt_arr.append(end_time-start_time)

            client_socket.close()
            client_socket=None
    except Exception as e:
        print(f'[rttTest measureRTT] error occured while measuring RTT:',e)
    # to check which process of server(computer) is faster
    if not server_thread_finished:
        this_process_faster=True
    st.join()
    return rtt_arr

def waitToSync(ip_addr,my_port_num,other_port_num,wait_time=WAIT_TIME_DEFAULT):
    global this_process_faster
    rtt_arr=measureRTT(ip_addr,my_port_num,other_port_num)
    #TEST
##    cur_time= time.time()
##    print(f'cur time:{cur_time}')
    
    avg_rtt=sum(rtt_arr)/len(rtt_arr)
    if this_process_faster:
        time.sleep(wait_time-avg_rtt/2)
    else:
        time.sleep(wait_time)

    cur_time= time.time()
    #DEBUG
    if this_process_faster:
        print('[waitToSync] me faster!')
    else:
        print('[waitToSync] me slower')
    #DEBUG
##    print(f'cur time:{cur_time}')
    return cur_time

##if __name__=='__main__':
##    print(f'cur_time:{time.time()}')
##    for _ in range(5): print(waitToSync(IP_ADDR,10,20))
    
