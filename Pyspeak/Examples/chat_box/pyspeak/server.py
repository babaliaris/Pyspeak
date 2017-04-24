import socket, struct

from select import select
from threading import Thread
from pyspeak.exceptions import ServerIpError
from pyspeak.exceptions import ServerRunError
from pyspeak.exceptions import ServerExistsError



class Server:

    #-_-_-_-_-_-_-_-_-_-_-_-_-_-_-Constructor-_-_-_-_-_-_-_-_-_-_-_-_-_-_-#
    def __init__(self, ip, port):
        '''Server Constructor --> Server object'''

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

        #Try to bind the socket.
        try:
            self.socket.bind( (ip, port) )
            pass

        #Ip was wrong.
        except socket.gaierror:
            error = 'Server failed to be enstablished due to wrong input.'\
            +'Please check ip and port.'


        #Port already in use.
        except OSError:
            error = 'Another server is already using the port you specified.'
            pass

        #Raise ServerIpError.
        if 'input' in error:
            raise ServerIpError(error)

        #Raise ServerExistsError.
        if 'Another' in error:
            raise ServerExistsError(error)

        #Start listening.
        self.socket.listen(1)

        #Sockets list.
        self.sockets = [self.socket]

        #Threads running flag.
        self.running = True

        #Requests.
        self.requests = []

        #Accepts.
        self.accepts = []

        #Connections.
        self.connectionsLost = []

        return
    #-_-_-_-_-_-_-_-_-_-_-_-_-_-_-Constructor-_-_-_-_-_-_-_-_-_-_-_-_-_-_-#





    #============================Server Thread============================#
    def __ServerThread__(self):
        '''This is the background functionality of the server.'''

        while True:

            #-------Wait until next network activity------#
            try:
                readable, writeable, excep = select(self.sockets,
                                                    [],
                                                    self.sockets)
                pass


            #Server closed.
            except OSError:
                break
            #-------Wait until next network activity------#
            


            #---------------Accept A Client---------------#
            if self.socket in readable:

                #Try to accept a client.
                try:
                    client, address = self.socket.accept()
                    pass

                #Server closed.
                except OSError:
                    break

                #Enable Nagle's argorithm for this client.
                client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

                #Append client into the sockets list.
                self.sockets.append(client)

                #Append a new accept.
                self.accepts.append(client)
                pass
            #---------------Accept A Client---------------#



            #----------------Receive Data-----------------#
            elif len(readable) > 0:

                for client in readable:

                    #Try to receive bytes.
                    try:
                        data = client.recv(65536)
                        pass

                    #The connection with the client was lost.
                    except ConnectionResetError:

                        #Append a connection.
                        if client not in self.connectionsLost:
                            self.connectionsLost.append(client)
                            pass
                        
                        continue


                    #The client closed the connection.
                    if len(data) == 0:

                        #Append a connection.
                        if client not in self.connectionsLost:
                            self.connectionsLost.append(client)
                            pass
                        
                        continue
                    

                    #Handle clients.
                    else:

                        #Append a new request.
                        self.requests.append( (client, data) )
            #----------------Receive Data-----------------#
                        
    #============================Server Thread============================#





    #===========================Handle Requests===========================#
    def __HandleRequests__(self):
        '''This Thread waits for a request and then is calling the
           __UnpackData__() method.'''

        while self.running:

            for request in self.requests:

                #Unpack data and call received().
                self.__UnpackData__(request[0], request[1])

                #Remove this request.
                self.requests.remove(request)
    #===========================Handle Requests===========================#






    #===========================Handle Accepts============================#
    def __HandleAccepts__(self):
        '''This Thread waits until the server accepts a client and then
           is calling the accepted() method.'''

        while self.running:

            for accept in self.accepts:

                #Call accepted()
                self.accepted(accept)

                #Remove this accept.
                self.accepts.remove(accept)
    #===========================Handle Accepts============================#






    #==========================Handle Connections=========================#
    def __HandleConnections__(self):
        '''This Thread waits until a client disconnects from the server
           and then is calling the connectionClosed() method.'''

        while self.running:

            for connection in self.connectionsLost:

                #Remove the client from the list.
                try:
                    self.sockets.remove(connection)
                    pass

                #This will accure if this thread and the Server Thread
                #are asynchronous. Then just continue, you don't have to
                #do anything.
                except ValueError:
                    self.connectionsLost.remove(connection)
                    continue

                #Call connectionClosed().
                self.connectionClosed(connection)

                #Remove this connection.
                self.connectionsLost.remove(connection)
    #==========================Handle Connections=========================#   
                





    #=============================Unpack Data=============================#
    def __UnpackData__(self, client, data):
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
            self.received(client, unpacked)
            pass
        pass
    #=============================Unpack Data=============================#





    #=================These Methods Need To Be Implemented================#
    def accepted(self, client):
        '''The server is calling this method every time a new client
           connects.'''
        pass

    def connectionClosed(self, client):
        '''The server is calling this method every time a client
           is closing the connection.'''
        pass

    def received(self, client, data):
        '''The server is calling this method every time a client
           sends requests.'''
        pass
    #=================These Methods Need To Be Implemented================#





    #================================Send=================================#
    def send(self, client, integer = 0, real = 0.0,
             boolean = False, string = ""):
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
            return client.send( buffer )

        #The server closed the connection.
        except ConnectionResetError:

            #Append a connection.
            if client not in self.connectionsLost:
                self.connectionsLost.append(client)
                pass

            return 0
    #================================Send=================================#





    #=============================Get Clients=============================#
    def getClients(self):
        '''Return a list with all the client sockets.'''
        return self.sockets[1:]
    #=============================Get Clients=============================#





    #================================Start================================#
    def run(self):
        '''Run the server.'''

        #Just a flag.a
        error = False

        #Try to run the server.
        try:
            
            #Start the server thread.
            thread = Thread(target = self.__ServerThread__)
            thread.start()

            #Start the handle requests thread.
            thread = Thread(target = self.__HandleRequests__)
            thread.start()

            #Start the handle accepts thread.
            thread = Thread(target = self.__HandleAccepts__)
            thread.start()

            #Start the handle connections thread.
            thread = Thread(target = self.__HandleConnections__)
            thread.start()
            pass

        #Server can't run.
        except RuntimeError:
            error = True
            pass

        #Raise ServerRunError.
        if error:
            raise ServerRunError('Server can\'t run because your'
                                 +' cpu reached maximum amount of threads.'
                                 +' Server need 5 threads to run.')
        pass
    #================================Start================================#





    #================================Stop=================================#
    def stop(self):
        '''Stop the server.'''
        self.socket.close()
        self.running = False
        pass
    #================================Stop=================================#
        
