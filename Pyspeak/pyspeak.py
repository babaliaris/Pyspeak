import sys, os, shutil

def copyModules(projectPath):

    #Error messanger.
    error = ''

    #Create paths.
    module1 = os.path.join('Main Modules', 'client_main.py')
    module2 = os.path.join('Main Modules', 'server_main.py')


    #Try opening midule1.
    try:
        fileRead1 = open(module1, 'rb')
        pass

    #Failed.
    except FileNotFoundError:
        error = 'The file: "'+module1+'" could not been found.'
        return error


    #Try opening module2.
    try:
        fileRead2 = open(module2, 'rb')
        pass

    #Failed.
    except FileNotFoundError:
        error = 'The file: "'+module2+'" could not been found.'
        return error


    #Create the two files.
    fileWrite1 = open(os.path.join(projectPath, 'client_main.py'), 'wb')
    fileWrite2 = open(os.path.join(projectPath, 'server_main.py'), 'wb')

    #Copy modules into the new files.
    fileWrite1.write( fileRead1.read() )
    fileWrite2.write( fileRead2.read() )

    #Close read files.
    fileRead1.close()
    fileRead2.close()

    #Close write files.
    fileWrite1.close()
    fileWrite2.close()
    return error




def createProject(path):

    #Error messanger.
    error = ''

    #Try to create the project folder.
    try:
        os.mkdir(path)
        pass


    #File not found error.
    except FileNotFoundError:
        error = 'The path you gave is not a valid path.'
        return error

    #File exists error.
    except FileExistsError:
        error = 'A folder already exists: '+path
        return error

    #Permission error.
    except PermissionError:
        error = 'Operate System denied access.'
        return error

    #Copy pyspeak.
    shutil.copytree( "pyspeak", os.path.join(path, "pyspeak") )

    #Copy modules.
    return copyModules(path)




if len(sys.argv) > 1:

    #Create the project.
    error = createProject( sys.argv[1] )

    #Handle any errors.
    if error != '':

        #Remove the project folder.
        if error != 'Operate System denied access.' and\
           "A folder already exists" not in error:
            shutil.rmtree(sys.argv[1])
            
        print()
        print(error)
        print()
        pass

    #Else, print success info.
    else:
        print()
        print("Project created successfully.")
        print()
        pass


else:
    print("Not enough arguments. (You must specify the project path).")
    input("Press ENTER to exit.")
    

    

    
