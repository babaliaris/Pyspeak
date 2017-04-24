import pyspeak

class Server(pyspeak.Server):

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

        #Go through all connected clients.
        for connected_client in self.getClients():

            #Send the message to all clients except the
            #one who send the request.
            if connected_client != client:

                #Send the string.
                self.send( connected_client, string = data[3] )
                pass
            pass
        pass



#Try to run the server.
try:
    
    #Create a server object.
    server = Server("192.168.1.4", 1996)

    #Run the server.
    server.run()
    pass

#Server could not run, because cpu is full of threads.
except pyspeak.ServerRunError:
    print("Server can't run because cpu is full of threads.")
    pass

#Server could not been established.
except pyspeak.ServerIpError:
    print("Server could not been established. Please check ip and port.")
    pass

#Port is already in use.
except pyspeak.ServerExistsError:
    print("Server could not been establised because the port is already in use.")


#-----------------------Write your code below--------------------------#
