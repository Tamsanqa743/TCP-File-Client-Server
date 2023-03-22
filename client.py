# TCP client for downloading and uploading files to a server
# Tamsanqa Thwala
# 22 March 2023
from socket import *
import os
from hashlib import blake2b



def init_client(server_port, server_ip):

    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    return client_socket

def sendFile(file_name, client_socket):
    '''handles sending of files to server given filename'''
    file_size = os.path.getsize(file_name) #Gets the fileSize dynamically

    with open(file_name, 'rb') as file:
        sent_size = 0
        while True:
            try:
                file_data = file.read(1024)
                sent_size += len(file_data)
                if not file_data:
                    break
                client_socket.sendall(file_data)
                if sent_size == file_size:
                    print('Transfer done')
                    break
            except Exception as e:
                print(e)
                break

    # client_socket.close()

def gen_hash(file):
    '''return hash of file using blake2b hashing algorithm'''
    hasher = blake2b(digest_size=20)
    with open(file,'rb') as file:

        data = 0
        while data != b'':
            # read only 1024 bytes at a time
            data = file.read(1024)
            hasher.update(data)

    # return the hex representation of digest
    return hasher.hexdigest()


def receiveFile(client_socket,file_name, fileSize):
    '''accepts connection and receives data from client'''

    file = open(file_name, 'wb') # open file
    received_size = 0
    while True:
        try:
            file_data = client_socket.recv(1024)
            received_size += len(file_data)
            if not file_data:
                break

            file.write(file_data)
            if fileSize == received_size:
                print('Transfer done')
                break
        except Exception as e:
            print(e)
            break

    file.close()

def main():
    server_ip = input("Enter server IP address:\n")
    server_port = int(input('Enter server port number:\n'))
    client_socket = init_client(server_port=server_port, server_ip=server_ip) # initialize client socket
    
    while True:
        choice = input("Choose an option: (u)pload, (d)ownload, (q)uery, (e)xit:\n") 

        if choice.lower() == 'u' or choice.lower() == 'upload':
            file_name = input("Enter file name:\n")
            file_size = os.path.getsize(file_name) #Gets the fileSize dynamically
            file_checksum = str(gen_hash(file_name)) # generate hash for file to be sent


            header = 'POST|' + str(file_size) + '|' + file_name + '|' + file_checksum
            client_socket.send(header.encode())
            sendFile(file_name, client_socket)


        if choice.lower() == 'd' or choice.lower() =='download':
            file_name = input("Enter file name:\n")
            
            header = 'GET|' + file_name + '|#|#'
            client_socket.send(header.encode())
            request_response = client_socket.recv(1024).decode().split('|')
            status = request_response[0] 

            if status == 'OK':
                file_size = int(request_response[1])
                file_checksum = request_response[3] 

                receiveFile(client_socket,file_name, file_size)
                recv_file_checksum = str(gen_hash(file_name)) # generate hash for downloaded file 

                if recv_file_checksum == file_checksum:
                    print('...File safe!...')

            elif status == 'ERR':
                print('An error occured!\nMake sure file is on server!')

        if choice.lower() == 'q' or choice.lower() == 'query':
            header = 'QUERY|#|#|#'
            client_socket.send(header.encode())
            print('Files available on server:\n')
            print(client_socket.recv(1024).decode())
            print('........................................................')

        if choice.lower() == 'e' or choice.lower() == 'exit':
            header = 'EXIT|#|#|#'
            client_socket.send(header.encode())
            break

        
if __name__ == '__main__':
    main()