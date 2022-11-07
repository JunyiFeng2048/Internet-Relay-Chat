import os
import signal
import socket
import threading

clientList = list()
roomList = list()


class user:
    def __init__(self, username, connection, address):
        self.username = username
        self.connection = connection
        self.address = address


class room:
    def __init__(self, roomName):
        self.roomName = roomName
        self.userList = list()


def sendMsg(clientSelf, msg):  # send msg to all clients except client itself
    for client in clientList:
        if client.connection.fileno() != clientSelf:
            client.connection.send(msg.encode())


def actions(data, newUser):  # execute the command from clients
    # while True:
    try:
        if data:
            if data[0:4] == '/msg':  # send a message to a room
                splits = data.split()
                roomName = splits[1]
                msg = splits[2]
                roomFound = False
                userInRoom = False
                for i in roomList:  # make sure the room exists
                    if i.roomName == roomName:
                        for k in i.userList:
                            if k.username == newUser.username:  # make sure this user is in room
                                userInRoom = True
                        if not userInRoom:
                            newUser.connection.send(bytes('user not in room', 'UTF-8'))
                            return
                        for j in i.userList:
                            j.connection.send(bytes("[" + roomName + "]-" + newUser.username + ": " + msg, 'UTF-8'))
                        roomFound = True
                        break
                if not roomFound:
                    newUser.connection.send(bytes('room not found', 'UTF-8'))

            if data[0:5] == '/quit':  # quit IRC
                print(newUser.username + ' has quit the IRC')
                for i in clientList:  # remove the client from clientList
                    if i.username is newUser.username:
                        clientList.remove(i)
                        break
                for i in roomList:  # remove the client from rooms
                    for j in i.userList:
                        if j.username is newUser.username:
                            i.userList.remove(j)
                            break
                newUser.connection.send(bytes('goodbye', 'UTF-8'))

            if data[0:7] == '/create':  # create a room
                roomName = data[8::]
                if roomName.isspace():
                    newUser.connection.send(bytes('format error', 'UTF-8'))
                    return
                for i in roomList:  # make sure the room does not exist
                    if i.roomName == roomName:
                        newUser.connection.send(bytes('room exists', 'UTF-8'))
                        return
                nrc = 'New room ' + roomName + ' created'
                print(nrc)
                newRoom = room(roomName)
                newRoom.userList.append(newUser)
                roomList.append(newRoom)
                newUser.connection.send(bytes(nrc, 'UTF-8'))

            if data[0:5] == '/join':  # join a room
                roomFound = False
                for i in roomList:  # make sure the room exists
                    if i.roomName == data[6::]:
                        for j in i.userList:
                            if j.username == newUser.username:
                                newUser.connection.send(bytes('You already in room ' + i.roomName, 'UTF-8'))
                                return
                        i.userList.append(newUser)
                        newUser.connection.send(bytes('Joined ' + i.roomName, 'UTF-8'))
                        roomFound = True
                        break
                if not roomFound:
                    newUser.connection.send(bytes('room not found', 'UTF-8'))

            if data[0:5] == '/lsrm':  # print all rooms
                strRoomList = []
                for i in roomList:
                    strRoomList.append(i.roomName)
                # print(strRoomList)
                strRoomList = str(strRoomList)
                newUser.connection.send(bytes(strRoomList, 'UTF-8'))

            if data[0:5] == '/lsur':  # print all users in a room
                roomFound = False
                roomName = data[6::]
                strRoomUsers = []
                for i in roomList:  # make sure the room exists
                    if i.roomName == roomName:
                        for j in i.userList:
                            strRoomUsers.append(j.username)
                        roomFound = True
                        strRoomUsers = str(strRoomUsers)
                        newUser.connection.send(bytes(strRoomUsers, 'UTF-8'))
                        break
                if not roomFound:
                    newUser.connection.send(bytes('room not found', 'UTF-8'))

            if data[0:6] == '/leave':  # leave a room
                roomFound = False
                userInRoom = False
                for i in roomList:
                    if i.roomName == data[7::]:
                        for j in i.userList:
                            if j.username == newUser.username:
                                newUser.connection.send(bytes('Left ' + i.roomName, 'UTF-8'))
                                i.userList.remove(newUser)
                                userInRoom = True
                        if not userInRoom:
                            newUser.connection.send(bytes('user not in room', 'UTF-8'))
                        roomFound = True
                        break

                if not roomFound:
                    newUser.connection.send(bytes('room not found', 'UTF-8'))

            if data[0:3] == '/pm':  # private message to a client
                splits = data.split()
                pmUser = splits[1]
                # print(pmUser)
                # for i in clientList:
                # print(i.username)
                msg = splits[2]
                userFound = False
                for i in clientList:  # make sure the client exist
                    if i.username == pmUser:
                        i.connection.send(bytes("[private message] from " + newUser.username + ": " + msg, 'UTF-8'))
                        newUser.connection.send(bytes("[private message] to " + i.username + ": " + msg, 'UTF-8'))
                        userFound = True
                        break
                if not userFound:
                    newUser.connection.send(bytes('user not found', 'UTF-8'))

    except IndexError:  # prevent splits error
        newUser.connection.send(bytes('format error', 'UTF-8'))
    except socket.error:
        newUser.connection.send(bytes('unknown error', 'UTF-8'))
        newUser.connection.close()
    except ConnectionError:
        print('\nServer closed\n')
        newUser.connection.send(bytes('Unknown Error', 'UTF-8'))
        newUser.connection.close()
        serverSocket.close()
        os.kill(os.getpid(), signal.SIGTERM)
        exit(0)


def initUser(newUser):  # initialize an user and keep receiving data from clients
    username = newUser.connection.recv(2048).decode()
    newUser.username = username
    clientList.append(newUser)
    print(username + ' has joined the IRC')  # prompt the server that a new client joined to IRC
    print('now active users: ')
    for i in range(len(clientList)):
        print(i + 1, '-', clientList[i].username)

    try:
        while True:
            data = newUser.connection.recv(2048)  # keep receive data from clients
            actions(data.decode("utf-8"), newUser)  # execute the command from clients

    except socket.error:
        sendMsg(newUser.connection.fileno(), newUser.username + " has left the IRC")
    except ConnectionError:
        print('\nServer closed\n')
        newUser.connection.send(bytes('Unknown Error', 'UTF-8'))
        newUser.connection.close()
        serverSocket.close()
        os.kill(os.getpid(), signal.SIGTERM)
        exit(0)


def listen(serverSocket):
    while True:
        try:
            serverSocket.listen()  # makes a socket ready for accepting connections
            connection, address = serverSocket.accept()
            newUser = user(None, connection, address)
            actionth = threading.Thread(target=initUser, args=(newUser,))  # initialize an user and keep receiving data from clients
            actionth.start()

        except socket.error:
            break
        except ConnectionError:
            print('\nServer closed\n')
            newUser.connection.send(bytes('Unknown Error', 'UTF-8'))
            newUser.connection.close()
            serverSocket.close()
            os.kill(os.getpid(), signal.SIGTERM)
            exit(0)


if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 8888
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET: IPV4,  SOCK_STREAM: TCP
    connected = False
    while not connected:
        try:
            serverSocket.bind((HOST, PORT))
            connected = True
        except socket.error:
            print("\nPort is not available!\n")
            os.kill(os.getpid(), signal.SIGTERM)
            serverSocket.close()
            exit(0)

    th = threading.Thread(target=listen, args=(serverSocket,))  # start thread
    th.start()
    serverRunning = 'Server is running. To terminate the server, enter "/quit" '
    q = 'False'
    while q != '/quit':  # server administrator can terminate the server
        print(serverRunning)
        q = input()
    os.kill(os.getpid(), signal.SIGTERM)  # kill this thread
    serverSocket.close()  # close socket connection
    exit(0)
