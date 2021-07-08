import sys
import os
import socket

IP_ADDR=''
PORT=3500
MAX_LISTEN_LEN=5
MAX_BUFFER_LEN=1024
#choose file path of recieved file in server
FILE_NAME='cat.mp4'

# we recieve file content in naive byte array form
if __name__ == '__main__':
    server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.bind(('',PORT))
    server_socket.listen(MAX_LISTEN_LEN)

    connection_socket,addr=server_socket.accept()

    data=connection_socket.recv(MAX_BUFFER_LEN).decode()
    print(data)
    """
    with open(FILE_NAME,'wb') as f:
        while True:
            data = connection_socket.recv(MAX_BUFFER_LEN)
            print('breakpoint')
            if not data:
                break
            f.write(data)
    """

    print('program exiting...')
