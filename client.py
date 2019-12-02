import socket
import threading
import sys

def receivemsgs(client):
	global clientconnection
	while clientconnection:        
		msg=client.recv(4096).decode()
		print (msg)
		if(msg == "server shut down"):
			print("The Server broke down,enter quit to exit gracefully")
			clientconnection = False
		elif(msg == 'sending_file'):
			with open('destination.txt', 'wb') as f:
				print ('file opened')
				while True:
					data = client.recv(4096).decode()
					print(data)
					if not data:
						break
					f.write(data.encode())
				f.close()
		if("Private_chat" in msg):
			msgs=msg.strip().split()
			receivedmsg=msgs[-1]   #caesar cipher decryption
			alp="abcdefghijklmnopqrstuvwxyz"
			decryptedmsg=''
			rm=str(receivedmsg)
			for eachLetter in receivedmsg:
				if eachLetter in alp:
					index = alp.index(eachLetter)
					crypting = (index - 3) % 26
					decryptedmsg+=alp[crypting]
			print (decryptedmsg +" is the decrypted msg")
		elif(msg=="logged out"):
			print("End")
			clientconnection=False
  
def sendoptions(username, client):
	global clientconnection
	while clientconnection:
		action=input()
		client.send(action.encode())
		if action=="quit":
			clientconnection = False
			print("logged out")
			

try:
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.connect(('localhost', 8080))
	clientconnection=True
	while clientconnection:
		username=input("Enter username ")
		#print(username)
		client.send(username.encode())
		data = client.recv(4096).decode()
		if (data !="Welcome"):
			print("Username already exists\n Enter  a new name\n")
		else:
			password = input("Enter password ")
			client.send(password.encode())
			print('\nWelcome '+ username)
			print(''' YOUR OPTIONS:
                	1. To list the online clients 
                		Syntax: [list_clients]
                	2. To create a room 
                		Syntax: [create_room <name_of_the_room>]
                	3. To list the rooms 
                		Syntax: [list_rooms]
                	4. To list the members in the room 
                		Syntax: [list_members <name_of_the_room>]
                	5. To join a room 
                		Syntax: [join_room <name_of_the_room>]
                	6. To leave a room 
                		Syntax: [quit_room <name_of_the_room>]
                	7. To broadcast a message 
                		Syntax: [broadcast <message>]
                	8. Group chat
                		Syntax: [group_chat <name_of_the_room> <message>]
                	9. Private chat
                		Syntax: [private_chat <client_name> <message>]
                	10. Request a file
                		Syntax:[file_transfer]
                	11. To Quit
                		Syntax: [quit]
                	''')
			print("Enter your option!")
			threading.Thread(target = receivemsgs, args = (client,)).start()
			sendoptions(username,client)
			break
except KeyboardInterrupt as ki:
    print("Bye")
except BrokenPipeError as bpe:
    print("Connection broke")
finally:
    client.send('quit'.encode())
    clientconnection = False
    client.shutdown(socket.SHUT_RDWR) #shutdown the RDWR of the socket.
    client.close()    #close socket
    sys.exit(1)

