import os
import signal
import socket
import threading


def printMenu():
    print("Available commands: ")
    print("/create [chatroom name]: create a new chatroom")  #########
    print("/join [chatroom name]: join a chatroom")  #########
    print("/msg [chatroom name] <msg>: send a public message to a chatroom")  #########
    print("/pm [username] <msg>: send a private message to an user")  #########
    print("/leave [chatroom name]: leave a chatroom")  #########
    print("/lsur [chatroom name]: print all members of a chatroom")  #########
    print("/lsrm: print all chatrooms")  #########
    print("/menu: print all available commands")  #########
    print("/quit: quit the IRC")  #########


def send(clientSocket):  # send data
    while True:
        try:
            clientInput = input()
            if clientInput == '/menu':
                printMenu()
            else:
                clientSocket.send(clientInput.encode())

        except ConnectionError:
            print('\nServer closed\n')
            os.kill(os.getpid(), signal.SIGTERM)
            exit(0)

        except socket.error:
            print("\nPort is not available\n")
            os.kill(os.getpid(), signal.SIGTERM)
            clientSocket.close()
            exit(0)


def receive(clientSocket):  # receive data
    while True:
        try:
            data = clientSocket.recv(2048)
            if data:
                temp = data.decode()
                if temp == 'goodbye':
                    print('Quit IRC')
                    os.kill(os.getpid(), signal.SIGTERM)
                    exit(0)
                elif temp == 'room exists':
                    print('Error. Room already exists')
                elif temp == 'room not found':
                    print('Error. Can not find room')
                elif temp == 'user not in room':
                    print('Error. You are not in the room')
                elif temp == 'user not found':
                    print('Error. Can not find the user')
                elif temp == 'format error':
                    print('Error. Command format is not correct')
                else:
                    print(temp)

        except ConnectionError:
            print('\nServer closed\n')
            os.kill(os.getpid(), signal.SIGTERM)
            exit(0)

        except socket.error:
            print("\nPort is not available\n")
            os.kill(os.getpid(), signal.SIGTERM)
            clientSocket.close()
            exit(0)


if __name__ == "__main__":
    try:
        HOST = '127.0.0.1'
        PORT = 8888
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET: IPV4,  SOCK_STREAM: TCP
        clientSocket.connect((HOST, PORT))

        username = input('Enter your username: ')
        clientSocket.send(username.encode())

        print("\t\t**************")
        print("\t\tWelcome to IRC")
        print("\t\t**************")
        printMenu()

        th1 = threading.Thread(target=send, args=(clientSocket,))
        th2 = threading.Thread(target=receive, args=(clientSocket,))
        th1.start()
        th2.start()

    except ConnectionError:
        print('\nServer closed\n')
        os.kill(os.getpid(), signal.SIGTERM)
        exit(0)

    except socket.error:
        print("\nPort is not available\n")
        os.kill(os.getpid(), signal.SIGTERM)
        clientSocket.close()
        exit(0)
