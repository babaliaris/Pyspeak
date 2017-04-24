class ServerIpError(Exception):
    '''Is been raised when the server can't connect to a specified ip.'''
    pass


class ServerExistsError(Exception):
    '''Is been raised when the port where the server tried to connect
       is already in use.'''
    pass


class ServerRunError(Exception):
    '''Is been raised when the server can't run.'''
    pass


class ClientConnectError(Exception):
    '''Is been raised when the client can't connect to a server.'''
    pass


class ClientRunError(Exception):
    '''Is been raised when the client can't run.'''
    pass
