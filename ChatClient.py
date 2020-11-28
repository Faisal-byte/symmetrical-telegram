#    15-112: Principles of Programming and Computer Science
#    HW07 Programming: Implementing a Chat Client
#    Name      : Faisal Mashhadi
#    AndrewID  : fmashhad

#    File Created: 20/10/2020

#    Modules
import socket
import tkinter



# Class chatComm. ipaddress and portnumber are 2 required fields
class chatComm:
    # Initialization
    def __init__(self,ipaddress,portnum):
        # this sets up the properties chatComm has
        self.ipaddress = ipaddress
        self.portnum = portnum
        self.socketConnection = self.startConnection()

    # Start Connection
    def startConnection(self):
        # return socketconnection property
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ipaddress, self.portnum))
        return s

    # 5 Helper functions for login function
    # Helper function (1) login
    def getM(self, password, challenge):
        # this function calculates the block and each chunk, then it is 
        # saved to M, and M is returned

        # Initialize variables
        message, block = password + challenge, ''

        # create the block
        while len(block) < (511 - len(message)):
            # keep adding message to block until it can't
            block += message
            if block == message:
                block += '1'

        while len(block) < 509:
            # keep adding 0's until the length is 3 less than 512
           block += '0'

        if len(message) < 100:
            # the last 3 digits are the length of message
            block += '0' + str(len(message))
        else: block += str(len(message))

        # create the 32-character chunk and M
        # Intialize variables
        M, chunks, TemporaryMessage, chunkSum = [], [], block, 0

        # loops through all characters in block
        for i in range(16):
            # make 16 chunks by dividing 520/32 where 32 characters are 
            # 1 chunk
            chunks.append(TemporaryMessage[:32])
            TemporaryMessage = TemporaryMessage[32:]

        for chunk in chunks:
            # loop through all the chunks and calculate their ASCII values
            chunkSum = 0
            for char in chunk:
                chunkSum += ord(char)
            # append the results to the list M
            M.append(chunkSum)

        return M

    # Helper function (2) login
    def leftrotate(self, x, c):
        # predefined function given by the question
        return (x << c)&0xFFFFFFFF | (x >> (32-c) & 0x7FFFFFFF >> (32-c))   

    # Helper function (3) login
    def getResult(self, a0,b0,c0,d0,A,B,C,D):
        # predefined function given by the question
        a0 = (a0 + A) & 0xFFFFFFFF
        b0 = (b0 + B) & 0xFFFFFFFF
        c0 = (c0 + C) & 0xFFFFFFFF
        d0 = (d0 + D) & 0xFFFFFFFF  
        return str(a0) + str(b0) + str(c0) + str(d0)

    # Helper function (4) login
    def getSandKValues(self):
        # predefined values for the lists s and K given by the question
        s = [7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
        5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20, 5, 9, 14, 20,
        4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
        6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21]

        K = [0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 
        0x4787c62a, 0xa8304613, 0xfd469501, 0x698098d8, 0x8b44f7af, 
        0xffff5bb1, 0x895cd7be, 0x6b901122, 0xfd987193, 0xa679438e, 
        0x49b40821, 0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
        0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8, 0x21e1cde6, 
        0xc33707d6, 0xf4d50d87, 0x455a14ed, 0xa9e3e905, 0xfcefa3f8, 
        0x676f02d9, 0x8d2a4c8a, 0xfffa3942, 0x8771f681, 0x6d9d6122, 
        0xfde5380c, 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
        0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05, 0xd9d4d039, 
        0xe6db99e5, 0x1fa27cf8, 0xc4ac5665, 0xf4292244, 0x432aff97, 
        0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92, 0xffeff47d, 
        0x85845dd1, 0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
        0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391]
        
        return s, K

    # Helper function (5) login
    def calculateHash(self, M, s, K):
        # this function generates a hash for the user 
        # to respond to the server's challenge

        # initialize variables
        a0, b0, c0, d0 = 0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476
        A, B, C, D = a0, b0, c0, d0
        results = []

        # loop through all chuncks and calculates the hash
        for i in range(64):
            if 0 <= i <= 15:
                F = (B & C) | ((~B) & D)
                F = F & 0xFFFFFFFF
                g = i
            elif 16 <= i <= 31:
                F = (D & B) | ((~D) & C)
                F = F & 0xFFFFFFFF
                g = (5*i + 1) % 16
            elif 32 <= i <= 47:
                F = B ^ C ^ D
                F = F & 0xFFFFFFFF
                g = (3*i + 5) % 16
            elif 48 <= i <= 63:
                F = C ^ (B | (~D))
                F = F & 0xFFFFFFFF
                g = (7*i) % 16

            dTemp, D, C = D, C, B
            B = B + self.leftrotate(A+F+K[i]+M[g], s[i])
            B = B & 0xFFFFFFFF
            A = dTemp

        return a0, b0, c0, d0, A, B, C, D


    # Login to server
    def login(self, username, password):
        # getting the challenge
        if username == '': return False
        if ' ' in username: return False
        comm = self.socketConnection
        comm.send(bytes('LOGIN {}\n'.format(username), 'utf-8'))
        challenge = str(comm.recv(1000), "utf-8").split()[2]
        # makes sure the username provided is in the server
        if 'FOUND' in challenge: return False

        # creating the block and M
        M = self.getM(password, challenge)

        # get the values of the tables s and K
        s, K = self.getSandKValues()

        # calculates hash of the password + challenge
        a0, b0, c0, d0, A, B, C, D = self.calculateHash(M, s, K)
        result = self.getResult(a0, b0, c0, d0, A, B, C, D)

        # sends the server the hash calculated and gets a response
        comm.send(bytes('LOGIN {} {}\n'.format(username, result), 'utf-8'))
        finalresponse = str(comm.recv(1000), "utf-8")

        if 'WRONG PASSWORD!' in finalresponse:
            return False
        return True

    # get active users 
    def getUsers(self):
        # returns a list of active users
        comm = self.socketConnection

        # gets the size of the message
        comm.send(bytes('@users\n','utf-8'))
        response = str(comm.recv(7), "utf-8")
        size = int(response.split('@')[1])

        # gets the active users as a list and returns it
        return str(comm.recv(size), "utf-8").split('@')[2:]

    # get friends 
    def getFriends(self):
        # returns a list of your friends
        comm = self.socketConnection

        # gets the size of the message
        comm.send(b'@friends')
        size = str(comm.recv(7), "utf-8")
        size = int(size.split('@')[1])
        # calls server again with known size for message
        return str(comm.recv(size), "utf-8").split('@')[2:]

    # sends friend request
    def sendFriendRequest(self, friend):
        # sends a request to the username friend
        comm = self.socketConnection
        # 17 is the length of string wihtout {} {} + length of size (00000) = 22
        size = str(22+len(friend))

        # make sure size is 5-digit
        while len(size) < 5:
            size = '0' + size
        # makes a string to send to the server
        request = '@{}@request@friend@{}\n'.format(size,friend)
        # sends the request to get friends as a list
        comm.send(bytes(request,'utf-8'))
        # server respond's
        response = str(comm.recv(33+len(friend)), "utf-8")

        # returns whether it was a succesfful request or not
        if '@ok' in  response:
            return True
        return False

    # accepts friend request 
    def acceptFriendRequest(self, friend):
        # accepts a request from the username friend

        # finds size of message
        comm = self.socketConnection
        size = str(21+len(friend))
        # make sure its 5 digits
        while len(size) < 5:
            size = '0' + size
        # send the message
        request = '@{}@accept@friend@{}\n'.format(size, friend)
        comm.send(bytes(request,'utf-8'))
        # get the response from the server
        response = str(comm.recv(50+len(friend)), "utf-8")
        if '@ok' in  response:
            return True
        return False

    # sends message 
    def sendMessage(self, friend, message):
        # this function sends a message to username friend
        comm = self.socketConnection
        # determines size of message
        size = str(len(friend) + len(message) + 16)
        # make sure its 5 digits
        while len(size) < 5:
            size = '0' + size
        # sends message to server
        request = '@{}@sendmsg@{}@{}\n'.format(size, friend, message)
        comm.send(bytes(request,'utf-8'))
        # checks if the attempt was successful or not
        response = str(comm.recv(100), "utf-8")
        if '@ok' in response:
            return True
        return False

    # Sendfile 
    def sendFile(self, friend, filename):
        comm = self.socketConnection
        # reads file content
        #comm.getFriends()
        content = []
        with open(filename, 'r') as file:
            line = file.readline()
            while line:
                content.append(line)
                line = file.readline()
        # save it to contentText
        contentText = ''
        for i in content:
            contentText += i
        # calculate size of the message
        size = str(19+len(friend)+len(filename)+len(contentText))
        while len(size) < 5:
            size = '0' + size

        # send the message
        request = '@{}@sendfile@{}@{}@{}\n'.format(size, friend, filename, contentText)
        comm.send(bytes(request, 'utf-8'))

        response = str(comm.recv(100), "utf-8")

        # checks if it was successful or not
        if '@ok' in response:
            return True
        return False

    # gets requests 
    def getRequests(self):
        comm = self.socketConnection
        # return a list of users who requested to become your friend
        comm.send(bytes('@rxrqst\n','utf-8'))
        size = int(str(comm.recv(7), "utf-8").split('@')[1])
        
        return str(comm.recv(size), "utf-8").split('@')[1:]

    # gets mail
    def getMail(self):
        # gets all messages and files sent to you
        comm = self.socketConnection
        # check size of message
        comm.send(bytes('@rxmsg\n','utf-8'))
        size = int(str(comm.recv(7), "utf-8").split('@')[1])
        response = str(comm.recv(size), "utf-8").split('@')

        # appends all messages to messages and files to files
        messages, files = [], []
        for char in range(len(response)):
            if response[char] == 'msg':
                messages.append([response[char+1], response[char+2]])
            elif response[char] == 'file':
                files.append([response[char+1], response[char+2]])

                # download the file to the current directory
                f = open(response[char+2], 'w+')
                for i in response[char+3]:
                    f.write(i)
                f.close()

        return (tuple(messages), tuple(files))
