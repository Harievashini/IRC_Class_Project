import socket
import sys
import threading

def server_action(client,addr):
    try:
        clientconnected= True
        while clientconnected:
            username=client.recv(4096).decode()
            print("username:" + username)
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
                    option=client.recv(4096).decode()
                    if "list_clients" in option:
                        users= clientusers.keys()
                        print(users)
                        online_users=''
                        for user in users:
                            online_users += user + "," 
                        client.send(online_users.encode())
                    elif "create_room" in option:
                        msg=option.partition(' ')[2]
                        print(msg) 
                        if msg in rooms.keys():
                            client.send("sorry, Room name already available. Enter another".encode())
                        else:
                            rooms.setdefault(msg, []).append(username)
                            print(rooms)
                            client.send("Room Created".encode())
                    elif "list_rooms" in option:
                        #print("Rooms")
                        all_rooms= rooms.keys()
                        print(all_rooms)
                        all_r=''
                        for r in all_rooms:
                            all_r += r + "," 
                        client.send(all_r.encode())
                    elif "list_members" in option:
                        msg=option.partition(' ')[2]
                        print(msg)
                        all_members=''
                        if msg in rooms.keys():
                            for member in rooms[msg]:
                                all_members+=str(member)+","
                            print(all_members)
                            client.send(all_members.encode())
                        else:
                            client.send("This room does not exist".encode())
                    elif "join_room" in option:
                        msg=option.partition(' ')[2]
                        print(msg)
                        if msg in rooms.keys():
                            if username in rooms[msg]:
                                client.send("already in the room".encode())
                            else:
                                rooms[msg].append(username)
                                client.send(("Added to " + msg).encode())
                        else:
                            client.send("This room does not exist".encode())
                        print(rooms)
                    elif "quit_room" in option:
                        msg=option.partition(' ')[2]
                        print(msg)
                        if msg in rooms.keys():
                            if username in rooms[msg]:
                                rooms[msg].remove(username) 
                                print(rooms)
                                client.send("Removed from the room".encode())  
                                for name in rooms[msg]:
                                    clientusers[name].send(str(username + ' has left the room - ' + msg).encode())
                                print(username + " left " + msg)       
                            else:
                                client.send("Not in this room,enter a valid room".encode())
                        else:
                            client.send("This room does not exist".encode())
                          
                    elif "broadcast" in option:
                        msg=option.partition(' ')[2]
                        print(msg)
                        for i in clientusers.keys():
                            if i== username:
                                continue
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
                    elif "file_transfer" in option:
                        print('Server transferring the file')
                        client.send('sending_file'.encode())
                        filename='source.txt'
                        f = open(filename,'rb')
                        l = f.read(4096)
                        while (l):
                            client.send(l)
                            print('Sent ',repr(l))
                            l = f.read(4096)
                        f.close()
                        print('Done sending')
                    elif "quit" in option:
                        clientusers.pop(username)
                        #print(clientusers)
                        for present in rooms:
                            if username in rooms[present]:
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
    clientusers={}
    passwords={}
    rooms={}
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv.bind(('localhost', 8080))
    print("server is binded...")
    serv.listen(5)
    print("server is listening...")
    while True:
        client, addr = serv.accept()
        print ("connection accepted")
        threading.Thread(target=server_action, args=(client,addr)).start()
except BrokenPipeError as bpe:
    print("Connection broke")
except KeyboardInterrupt as ki:
    print("Server gracefully shuts down")
    for username,client in clientusers.items():
        client.send("server shut down".encode()) #--> request each client to quit, the client replies with **quit, control flows to quit module, client thread closes
    #serv.shutdown(socket.SHUT_RDWR)
    serv.close()
    sys.exit(1)


