import pyspeak

class Client(pyspeak.Client):

    def connected(self, client):
        '''The client is calling this method when the server
           accepts him (only once).'''
        pass

    def connectionClosed(self, client):
        '''The client is calling this method when the server closes
           the connection (only once).'''

    def received(self, client, data):
        '''The client is calling this method every time the server
           sends requests.'''
        print( data[3] )
        pass



#Try to run the server.
try:
    
    #Create a server object.
    client = Client("192.168.1.4", 1996)

    #Run the server.
    client.run()
    pass

#Client could not run, because cpu is full of threads.
except pyspeak.ClientRunError:
    print("Client can't run because cpu is full of threads.")
    pass

#Client could not connect.
except pyspeak.ClientConnectError:
    print("Client could not connect to the server. Please check ip and port.")


#-----------------------Write your code below--------------------------#

while True:

    #Get the message.
    message = input()

    #Stop the program.
    if message == "/stop":
        client.stop()
        break

    #Else send the message.
    client.send(string = message)

