import socket, struct

from threading import Thread
from pyspeak.exceptions import ClientConnectError
from pyspeak.exceptions import ClientRunError

class Client:

    #-_-_-_-_-_-_-_-_-_-_-_-_-_-_-Constructor-_-_-_-_-_-_-_-_-_-_-_-_-_-_-#
    def __init__(self, ip, port):
        '''Client Constructor --> Client object'''

        #Ip error.
        if type(ip) != str:
            typo = str(type(ip))[7:].replace("'", "").replace(">","")
            raise AttributeError('Attribute: "ip", must be type of str not '+\
                                 typo+'.')

        #Port error.
        if type(port) != int:
            typo = str(type(port))[7:].replace("'", "").replace(">","")
            raise AttributeError('Attribute: "port", must be type of int not'\
                                 +' '+typo+'.')



        #Create the socket object.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #Enable nodelay messages (Nagle's Algorithm).
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)


        #Error message.
        error = ''

        #Try connecting.
        try:
            self.socket.connect( (ip, port) )
            pass

        #Wrong ip, port.
        except ConnectionRefusedError:
            error = 'Failed to connect. Please check ip and port.'\
                    +' Also make sure that the server is running.'
            pass

        #Raise ClientConnectError.
        if error != '':
            raise ClientConnectError(error)

        #Threads flag.
        self.running = True

        #Requests.
        self.requests = []
        return
    #-_-_-_-_-_-_-_-_-_-_-_-_-_-_-Constructor-_-_-_-_-_-_-_-_-_-_-_-_-_-_-#





    #============================Client Thread============================#
    def __ClientThread__(self):
        '''This is the background functionality of the client.'''

        while True:


            #Try to receive data.
            try:
                data = self.socket.recv(65536)
                pass

            #Server closed the connection.
            except ConnectionResetError:
                self.connectionClosed(self.socket)
                self.running = False
                break

            #Client closed the connection.
            except ConnectionAbortedError:
                break


            #Connection Closed.
            if len(data) == 0:
                self.connectionClosed(self.socket)
                self.running = False
                break
            
            #Append a request.
            self.requests.append(data)
    #============================Client Thread============================#





    #===========================Handle Requests===========================#
    def __HandleRequests__(self):
        '''This Thread waits for a request and then is calling the
           received() method.'''

        while self.running:

            for request in self.requests:

                #Unpack data and call received().
                self.__UnpackData__(self.socket, request)

                #Remove this request.
                self.requests.remove(request)
    #===========================Handle Requests===========================#





    #=============================Unpack Data=============================#
    def __UnpackData__(self, server, data):
        '''This method unpacks the data from bytes to Data Types and
           then calls the received() method.'''

        while len(data) > 0:

            #Get the first 3 values.
            integer = struct.unpack('i', data[:4] ) [0]
            real    = struct.unpack('f', data[4:8] )[0]
            boolean = struct.unpack('?', data[8:9] )[0]

            #Remove first 9 bytes from the buffer.
            data    = data[9:]

            #----------Create The String----------#
            string = ''

            ch     = bytes.decode(data[:1]) #Get a character from the buffer.
            data   = data[1:]               #Remove that one byte.

            #Keep until you find the marker.
            while ch != '\0':
                string += ch                    #Add it on the string.
                ch     = bytes.decode(data[:1]) #Move to the next character.
                data   = data[1:]               #Remove that character.
                pass
            #----------Create The String----------#
            

            #Create the data.
            unpacked = (integer, real, boolean, string)

            #Call Received.
            self.received(server, unpacked)
            pass
        pass
    #=============================Unpack Data=============================#





    #=================These Methods Need To Be Implemented================#
    def connected(self, server):
        '''The client is calling this method when the server
           accepts him (only once).'''
        pass

    def connectionClosed(self, server):
        '''The client is calling this method when the server closes
           the connection (only once).'''
        pass

    def received(self, server, data):
        '''The client is calling this method every time the server
           sends requests.'''
        pass
    #=================These Methods Need To Be Implemented================#





    #================================Send=================================#
    def send(self, integer = 0, real = 0.0, boolean = False, string = ""):
        '''Send an integer, real, boolean and a string.'''

        #Integer error.
        if type(integer) != int:
            typo = str(type(integer))[7:].replace("'", "").replace(">","")
            raise AttributeError('Attribute: "integer" must be type of int'+
                                 ' not '+typo)

        #Real error.
        if type(real) != float:
            typo = str(type(real))[7:].replace("'", "").replace(">","")
            raise AttributeError('Attribute: "real" must be type of float'+
                                 ' not '+typo)

        #Boolean error.
        if type(boolean) != bool:
            typo = str(type(boolean))[7:].replace("'", "").replace(">","")
            raise AttributeError('Attribute: "boolean" must be type of bool'+
                                 ' not '+typo)

        #String error.
        if type(string) != str:
            typo = str(type(string))[7:].replace("'", "").replace(">","")
            raise AttributeError('Attribute: "string" must be type of str'+
                                 ' not '+typo)


        #String is very big.
        if len(string) > 1000:
            raise ValueError('Attribute: "string" must have a'
                             +' size of 1000 max.')


        #Set a market on the string.
        string += '\0'

        #Create the buffer. 4(integer) + 4(float) + 1(boolean)
        #+ 1001(string) = 1010 bytes (max size of buffer).
        buffer = struct.pack('i', integer) +\
                 struct.pack('f', real) +\
                 struct.pack('?', boolean) +\
                 str.encode(string)

        #Send and return the sended bytes.
        try:
            return self.socket.send( buffer )

        #The server closed the connection.
        except ConnectionResetError:
            return 0
    #================================Send=================================#





    #================================Start================================#
    def run(self):
        '''Run the client.'''

        #Just a flag.
        error = False

        #Try to run.
        try:
            
            #Run the client thread.
            thread = Thread(target = self.__ClientThread__)
            thread.start()

            #Run the handle requests thread.
            thread = Thread(target = self.__HandleRequests__)
            thread.start()

            #Call the connected method.
            self.connected(self.socket)
            pass

        #Failed.
        except RuntimeError:
            error = True
            pass

        #Raise ClientRunError.
        if error:
            raise ClientRunError('Client can\'t run because your'
                                 +' cpu reached maximum amount of threads.'
                                 +' Client need 3 threads to run.')
            
        pass
    #================================Start================================#





    #================================Stop=================================#
    def stop(self):
        '''Stop the client.'''
        self.socket.close()
        self.running = False
        pass
    #================================Stop=================================#
        
