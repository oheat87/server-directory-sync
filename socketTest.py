import sys
import socket
import threading
from time import sleep

MAX_LISTEN = 5
MAX_BUFFER_LEN= 1024
IP_ADDR = '127.0.0.1'

class server_thread(threading.Thread):
    def __init__(self,name, socket):
        super().__init__()
        self.name = name
        self.server_socket=  socket

    def run(self):
        print('server thread start ', threading.currentThread().getName())
        print('waiting for client... ',threading.currentThread().getName())
        connection_socket,addr = self.server_socket.accept()
        print('access from',str(addr),'accepted')
        while True:
            data = connection_socket.recv(MAX_BUFFER_LEN)
            msg= data.decode('utf-8')
            if msg=='quit': break
            
            print('stranger:',msg)
            connection_socket.send('accepted'.encode('utf-8'))
            
        self.server_socket.close()
        print('server thread end ', threading.currentThread().getName())

class client_thread(threading.Thread):
    def __init__(self,name,ip_addr,port_num):
        super().__init__()
        self.name = name
        self.ip_addr= ip_addr
        self.port_num= port_num

    def run(self):
        print('client thread start ', threading.currentThread().getName())

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('trying to find server...','[',threading.currentThread().getName(),']')
        while True:
            try:
                client_socket.connect((self.ip_addr,self.port_num))
            except:
                sleep(0.001)
                continue
            break
        print('connected to server!','[',threading.currentThread().getName(),']')
        
        while True:
##            print('you: ',end='')
            msg= sys.stdin.readline().rstrip('\n')
            if msg=='quit':
                break
            client_socket.sendall(msg.encode())

            response_msg = client_socket.recv(MAX_BUFFER_LEN).decode()
            if response_msg!='accepted':
                print('error occurs sending message')         
            
        self.server_socket.close()
        print('client thread end ', threading.currentThread().getName())
        

if __name__ == '__main__':
    send_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', int(sys.argv[1])))
    server_socket.listen(MAX_LISTEN)

    st= server_thread('ST',server_socket)
    st.start()

    ct= client_thread('CT',IP_ADDR,int(sys.argv[2]))
    ct.start()

    st.join()
    ct.join()
    print('end entire program')
    
        

    
