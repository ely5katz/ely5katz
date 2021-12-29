from socket import *
import sys
import time
import struct
import select
import random
from threading import Thread
import scapy.all

GAME_PORT = 2090 # THE IP WHERE THE GAME WILL TAKE PLACE
BROADCASE_PORT = 13117 # THE IP WHERE BROADCASE IS HAPPENING
UDP_PORT = 14001

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_ip(eth):
    try:
        if eth == 1:
            ip = scapy.all.get_if_addr("eth1")
            return ip 
        if eth == 2:
            ip = scapy.all.get_if_addr("eth2")
            return ip
    except : pass
#HOST = gethostbyname(gethostname())
HOST = get_ip(1)

class Server:
    def __init__(self):
        self.udp = socket(AF_INET, SOCK_DGRAM)
        self.udp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        #self.udp.bind(('', UDP_PORT))
        self.udp.bind((HOST, UDP_PORT))

        self.tcp = socket(AF_INET, SOCK_STREAM)
        self.tcp.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.tcp.bind(('', GAME_PORT))
        self.tcp.listen(10)
        
        self.MAX_CONNECTIONS = 2 # 2 maximum players
        self.team_sockets = []
        self.team_names = {}
        self.questions = [("What is Our hackathon grade divided by 50?", 2), ("How many pizza slices nizan can eat?", 8),
        ("What is yossi's record of killing mosquitoes in a minute?", 4), ("from 0 to 9, how much you enjoyed our server?",9),
        ("How many welcoming sockets there is on a client?", 0), ("4 * 8 * 9 * 21 * 0 * 3 * 4 + 5 ?", 5),("What is length of the answer to this qustion?", 1)]

    def __broadcast(self):

        
        print(bcolors.OKCYAN+ f"Server started, listening on IP address {HOST}")
        password = struct.pack('ii', 5810, GAME_PORT) # this is the password the verify it came from the right server
        
        while not self.__full(): # wait for MAX_CONNECTIONS to be filled 
            
            try: self.udp.sendto(password, ('<broadcast>', BROADCASE_PORT))
            except: pass
            time.sleep(1)
                    
    def __full(self):
        self.__remove_disconnected()
        return len(self.team_sockets) == self.MAX_CONNECTIONS 
    
    def __remove_disconnected(self):
        
        to_remove = []
        for socket in self.team_sockets:
            try:
                socket.send("check".encode())
            except:
                to_remove.append(socket)
                
        for socket in to_remove:
            print(bcolors.FAIL+f"Team {self.get_team_name(socket)} Disconnected") # PRINT TEAM NAME
            del self.team_names[socket]
            self.team_sockets.remove(socket)
                
    def get_team_name(self, socket):
        return self.team_names[socket]
         
        
    def __receive_teams(self):
        while not self.__full():
            try:
                socket, address = self.tcp.accept()
                if not self.__full():
                    socket.setblocking(0)
                    team_name = socket.recv(2048).decode()
                    print(bcolors.OKBLUE+f"Team {team_name} Connected!")
                    self.team_names[socket] = team_name
                    self.team_sockets.append(socket)
            except:
                pass
    

            
    def init_game(self):
        broadcast_thread = Thread(target=self.__broadcast)
        receive_thread = Thread(target=self.__receive_teams)
        
        broadcast_thread.start()
        receive_thread.start()
        
        broadcast_thread.join()
        receive_thread.join()
        time.sleep(2)
        if not self.__full():
            print("Not enough players... waiting for new players")
            self.init_game()
        else:
            self.__play()
        
    
        
        
    
    def __play(self):
        global GAME_PORT
        print()
        welcome_message = bcolors.HEADER+'\nWelcome to Quick Maths.\n'
        welcome_message += f'Player 1: {self.get_team_name(self.team_sockets[0])}'
        welcome_message += f'Player 2: {self.get_team_name(self.team_sockets[1])}'
        welcome_message += '==\n'
        welcome_message += 'Please answer the following question as fast as you can:\n'
        
        queAns = random.choice(self.questions)
        que = queAns[0]
        ans = queAns[1]
        welcome_message += '\n' + bcolors.OKCYAN+que + '\n'
        # print(welcome_message)
        for socket in self.team_sockets:
            socket.sendall(welcome_message.encode())
        flag = True 
        while flag:
            read_sockets, write_sockets, error_sockets = select.select([socket for socket in self.team_sockets], [], [], 10)
            if len(read_sockets) == 0:
                break
            for socket in read_sockets:
                answer = socket.recv(1024).decode()
                try:
                    if int(answer) == ans:
                        winner = self.get_team_name(socket)
                        ansone = winner
                        flag = False
                    else:
                        for teamName in self.team_names.values():
                            if teamName != self.get_team_name(socket):
                                winner = teamName
                                flag = False
                            else:
                                ansone = teamName
                except:
                    pass
                
            # answer = socket.recv(1024).decode()
        if flag == True:
            for socket in self.team_sockets:
                socket.sendall(str(bcolors.OKGREEN+f"It's a draw \nThe correct answer was: {ans}").encode())
        else:
        # declare winner!
            messi = ansone + f" answered first and his answer is {answer} \nThe corret answer is: {ans} \nThe winner is: {winner} \n"
            for socket in self.team_sockets:
                socket.sendall(str(bcolors.OKGREEN+messi).encode())

        self.tcp.shutdown(1)
        self.tcp.close()
        self.udp.close()
        ###
        GAME_PORT = GAME_PORT+1
        time.sleep(3)
        server = Server()
        server.init_game()
                
            
      
            

server = Server()
server.init_game()
