# TCP server
# Tamsanqa Thwala
# 22 March 2023

from socket import *
import os
from hashlib import blake2b
from threading import Thread


def init_server(server_ip):
    '''Initializes server and return the server socket'''
    server_port = 12000
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(1)

    print("server is running....")
    return server_socket


def receive(connection_socket,filename, fileSize):
    '''accepts connection and receives data from client'''

    file = open('./Files/'+ filename, 'wb') # open file
    received_size = 0
    while True:
        try:
            file_data = connection_socket.recv(1024)
            received_size += len(file_data)
            if not file_data:
                break
            file.write(file_data)
            if received_size == fileSize:
                print('received')
                break
        except Exception as e:
            print(e)
            break

    file.close()

def closeConnection(connection_socket):
    '''Closes the connection to the client '''
    connection_socket.close()


def makeFileDir(current_directory):
    '''create Files directory for storing files'''
    if not os.path.exists(current_directory+'/Files'):
        try:
            os.mkdir('Files')
        except:
            print('An error occurred while creating directory!')


def gen_hash(file):
    '''return hash of file using blake2b hashing algorithm'''
    hasher = blake2b(digest_size=20)
    with open('./Files/' + file,'rb') as file:

        data = 0
        while data != b'':
            # read only 1024 bytes at a time
            data = file.read(1024)
            hasher.update(data)

    # return the hex representation of digest
    return hasher.hexdigest()

def query(current_directory):
    
    '''Get files in the current directory'''
    files = os.listdir(current_directory + '/Files')
    files_list = ''
    for item in files:
        files_list += item +'\n'

    return files_list.strip()


def sendFile(connection_socket, file_name, file_size):

    '''function sends requested file to client'''

    with open('./Files/' + file_name, 'rb') as file:
        sent_size = 0
        while True:
            try:
                file_data = file.read(1024)
                sent_size += len(file_data)
                if not file_data:
                    break
                connection_socket.sendall(file_data)
                if sent_size == file_size:
                    break
            except Exception as e:
                print(e)
                break
        file.close()


def handle_client(connection_socket, current_directory, addr):

    while True:
        
        request_data = connection_socket.recv(1024).decode().split('|')
        print(f'{addr}\'s current request:', request_data)
        command = request_data[0] # extract request command
        
        if command == 'QUERY':
            files_list = query(current_directory) # get files stored on server
            if files_list:
                connection_socket.send(files_list.encode())
            else:
                connection_socket.send('No files on server!'.encode())

        elif command == 'POST':
            # receive  file from client
            file_size = int(request_data[1])
            file_name = request_data[2]
            file_checksum = request_data[3]

            receive(connection_socket,file_name, file_size) # receive file data and save it to files folder


            # generate file checksum
            received_file_checksum = str(gen_hash(file_name))
            
            if received_file_checksum == file_checksum:
                print("File not tempered with!")
            else:
                print('There is a problem with the file!\nPlease retry upload')

            # send a done message to indicate file received successfully

        elif command == 'GET':
            file_name = request_data[1] # get file name from request data

            if os.path.exists(current_directory + '/Files/' + file_name):
                #  if the file exists
                file_size = os.path.getsize('./Files/' + file_name) #Gets the fileSize dynamically
                file_checksum = str(gen_hash(file_name)) # generate file checksum
                header = 'OK|' + str(file_size) + '|' + file_name + '|' + file_checksum
                connection_socket.send(header.encode()) # send filename and filesize to client
                sendFile(connection_socket,file_name, file_size)
            else:
                # file not found
                header = 'ERR|#|#|#'
                connection_socket.send(header.encode())

        elif command == 'EXIT':
            #close the connection
            closeConnection(connection_socket)
            print(f'Connection with client {addr} closed!')
            break

def main():
    '''main method'''
    current_directory = os.getcwd() # get current working directory
    makeFileDir(current_directory) # make Files directory
    
    server_ip = input("Enter server IP address:\n")

    server_socket = init_server(server_ip) # initialize server and return server socket
    print('The server is ready to receive')

    while True:
        client_connection, addr = server_socket.accept()
        thread = Thread(target=handle_client, args=(client_connection, current_directory,addr,))
        thread.start()


if __name__ == '__main__':
    # call main method
    main()