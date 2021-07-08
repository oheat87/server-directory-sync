import sys
import os
import socket

IP_ADDR='127.0.0.1'
PORT=3500
MAX_LISTEN_LEN=5
MAX_BUFFER_LEN=1024
FILE_NAME='file.txt'
#choose file path of being sended file in client
FILE_PATH='C:\\Users\\user\\PycharmProjects\\Intern\\serverA_test'

# we send file content in naive byte array form
if __name__ == '__main__':
    client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        client_socket.connect((IP_ADDR,PORT))
        print('connected to server')
        filelist=str(os.listdir(FILE_PATH)).encode()
        client_socket.sendall(filelist)
        """
        try:
            with open(FILE_PATH,'rb') as f:
                while True:
                    data=f.read(MAX_BUFFER_LEN)
                    if not data:
                        break
                    client_socket.sendall(data)
            
        except OSError as e:
            print('there is no such file:',e)
        """

        client_socket.close()
        print('successfully completed to send file content')
                
    except socket.error as e:
        print('there is no server open:',e)
        sys.exit(1)
    print('program exiting...')
