#server IRC program
#By Harie Vashini and Devyani

#importing libraries
import socket
import threading

#server actions to client requests
def server_action(client,addr):
    try:
        clientconnected= True
        while clientconnected:
            #receiving the username from the clients with user instance "client"
            username=client.recv(4096).decode()
            print("username:" + username)
            #checks the clients dictionary if the username already exists
            if(username in clientusers):
                client.send("username exists".encode())
            else:
                client.send("Welcome".encode())
                passwrd = client.recv(4096).decode()
                print(username+" is connected")
                clientusers[username] = client
                passwords[username] = passwrd
                clientconnection = True
                while clientconnection:
                    #receiving the options from the client
                    option=client.recv(4096).decode()
                    if "list_clients" in option:
                        users= clientusers.keys()
                        print(users)
                        online_users=''
                        for user in users:
                            online_users += user + "," 
                            #send list of online clients to the user through "client" instance
                        client.send(online_users.encode())
                        
                    elif "create_room" in option:
                        msg=option.partition(' ')[2]
                        print(msg) 
                        #check if the room exists by checking the keys from rooms list
                        if msg in rooms.keys():
                            client.send("sorry, Room name already available. Enter another".encode())
                        else:
                            #create the room with the name sent by the client and append the name of the client to the room
                            rooms.setdefault(msg, []).append(username)
                            print(rooms)
                            #send the message to the client
                            client.send("Room Created".encode())
                    elif "list_rooms" in option:
                        all_rooms= rooms.keys()
                        print(all_rooms)
                        all_r=''
                        for r in all_rooms:
                            all_r += r + "," 
                        #send the list to client
                        client.send(all_r.encode())
                    elif "list_members" in option:
                        msg=option.partition(' ')[2]
                        print(msg)
                        #create a list for members of the room
                        all_members=''
                        if msg in rooms.keys():
                            for member in rooms[msg]:
                                all_members+=str(member)+","
                            print(all_members)
                            #send the list of active members of the room to the client
                            client.send(all_members.encode())
                        else:
                            client.send("This room does not exist".encode())
                    elif "join_room" in option:
                        msg=option.partition(' ')[2]
                        print(msg)
                        #check if the room exists
                        if msg in rooms.keys():
                            #check if the user already exists in the room
                            if username in rooms[msg]:
                                client.send("already in the room".encode())
                            else:
                                #append username to the rooms dictionary
                                rooms[msg].append(username)
                                client.send(("Added to " + msg).encode())
                        else:
                            client.send("This room does not exist".encode())
                        print(rooms)
                    elif "quit_room" in option:
                        msg=option.partition(' ')[2]
                        print(msg)
                        #check the rooms list if the room provided by the client exists
                        if msg in rooms.keys():
                            #if username exists in the room
                            if username in rooms[msg]:
                                #remove the user from the given room
                                rooms[msg].remove(username) 
                                print(rooms)
                                client.send("Removed from the room".encode())  
                                for name in rooms[msg]:
                                    #send the name of the user who quit to other members of the room
                                    clientusers[name].send(str(username + ' has left the room - ' + msg).encode())
                                print(username + " left " + msg)       
                            else:
                                client.send("Not in this room,enter a valid room".encode())
                        else:
                            client.send("This room does not exist".encode())
                          
                    elif "broadcast" in option:
                        msg=option.partition(' ')[2]
                        print(msg)
                        #get active clients from the clientusers list
                        for i in clientusers.keys():
                            if i== username:
                                continue
                                #send the message to active clients
                            clientusers[i].send(str(msg + " from " + username).encode())
                        print(username + " broadcasted the message:" + msg)
            
                    elif  "group_chat" in option:
                        msgs=option.strip().split()
                        roomname=msgs[1]
                        msg=msgs[2:]
                        msge = ' '.join(msg)
                        print("Group chat message-"+msge)
                        if roomname in rooms.keys():
                            if username in rooms[roomname]:
                                for uname in rooms[roomname]:
                                    clientusers[uname].send(str("from "+username + ':' + msge).encode())
                            
                            else:
                                client.send("You are not a member, type a valid room name".encode())
                    #server provides secure private chat
                    #using caesar cipher algorithm for secure transfer with key =3
                    elif "private_chat" in option:
                        secure_key=3
                        alp="abcdefghijklmnopqrstuvwxyz" #for encryption and decryption
                        msgs=option.strip().split()
                        pier=msgs[1]
                        msg=msgs[2:]
                        msge = ' '.join(msg)
                        print("message - "+msge)
                        encryptedmsg=''
                        for eachLetter in msge:
                            if eachLetter in alp:
                                index = alp.index(eachLetter)
                                crypting = (index + 3) % 26
                                encryptedmsg+=alp[crypting]
                            elif(eachLetter==' '):
                                crypting=' '
                                encryptedmsg+=crypting
                        print (encryptedmsg +"- encrypted msg")
                        if pier in clientusers.keys():
                            clientusers[pier].send(str("Private_chat from "+username+" : "+encryptedmsg).encode())
                            print("Message successfully sent to " + pier)
                        else:
                            client.send("client not found")
                      #transferring the file to the client      
                    elif "file_transfer" in option:
                        print('Server transferring the file')
                        #acknowledge the client 
                        client.send('sending_file'.encode())
                        filename='source.txt'
                        #open the file specified
                        f = open(filename,'rb')
                        l = f.read(4096)
                        while (l):
                            client.send(l)
                            print('Sent ',repr(l))
                            l = f.read(4096)
                        f.close()
                        print('Done sending')
                    elif "quit" in option:
                        #pop the username from the clientusers dictionary
                        clientusers.pop(username)
                        #check if the user is present in any room
                        for present in rooms:
                            if username in rooms[present]:
                                #remove the user from the room
                                rooms[present].remove(username)
                        client.send("logged out".encode())
                        print(username + " has been logged out")
                        clientconnection = False 
                        clientconnected=False
                        
                    else:
                        client.send("sorry,type a valid option".encode())
    except:
        clientusers.pop(username)
        for present in rooms:
            if username in rooms[present]:
                rooms[present].remove(username)
        print(username + " has been logged out")
        print(clientusers.keys())
        clientconnection = False
        clientconnected=False           
        
try:
    #dictionary to keep track of active clients using key value pairs
    clientusers={}
    passwords={}
    rooms={}
    #establish the socket connection
    #AF_INET is the address domain of the socket
    #SOCK_STREAM is a type of socket allowing data or characters to be read in a continuous flow
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #binding to the open port
    serv.bind(('localhost', 8080))
    print("server is binded...")
    #the server is listening for 5 active connections
    serv.listen(5)
    print("server is listening...")
    while True:
        #client: socket instance for the user
        #addr: address of the user
        client, addr = serv.accept()
        print ("connection accepted")
        #creating threads for different connections
        #calling the method server_action()
        threading.Thread(target=server_action, args=(client,addr)).start()
except BrokenPipeError as bpe:
    print("Connection broke")
except KeyboardInterrupt as ki:
    print("Server gracefully shuts down")
    #sending message to all connected clients about server shutdown
    for username,client in clientusers.items():
        client.send("server shut down".encode())
    serv.close() #close socket
    


