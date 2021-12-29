from socket import *
import time
import struct
import getch
from multiprocessing import Process, Value
import psutil
import sys
import select
# import keyboard
# CLIENT = gethostbyname(gethostname())
#CLIENT = '20.100.102.12'
# broadcast port = udp port
BROADCAST_PORT = 13119
size = 1024

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

class Client:
    def __init__(self, team_name):
        self.udp = socket(AF_INET, SOCK_DGRAM)
        self.tcp = socket(AF_INET, SOCK_STREAM)
        self.team_name = team_name
    
    def search_host(self):
        self.udp.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.udp.bind(('172.99.255.255', BROADCAST_PORT))
        print(bcolors.OKCYAN+'Client started, listening for offer requests...')
        while True:
            
            try:
                message ,address = self.udp.recvfrom(size)
                
                #print(address)

                cookie, typ, port = struct.unpack('=IbH', message)
                #print(password, port)
            except:
                continue
                # We are about to play! let's connect to server.'''
            print(bcolors.WARNING+f"Received offer from {address[0]}, attempting to connect...")
            
            try:
                self.tcp.connect((address[0], port))
                print("Connected!")
                self.tcp.send(f'{self.team_name}\n'.encode())
                self.play()
            except: 
                print(address[0], port)
                client = Client("Rick&Rick cause we are both genius")
                client.search_host()

    def play(self):
        #p = Process(target= self.play_sync)
        #p.start()
        self.play_sync()
        Flagos = True
        while Flagos:
            readable, writeable, _ = select.select([sys.stdin, self.tcp], [], [])
            for r in readable:
                if r is sys.stdin:
                    writeable.append(self.tcp)
                    msg = r.readline()
                    Flagos = False
                    break
                if r is self.tcp:
                    masi =  r.recv(size).decode()
                    if masi != 'checked':
                        print(masi)
                        Flagos = False
                        break
            for w in writeable:
                w.sendall(msg.encode())
            time.sleep(0.5)
        winner_message = self.tcp.recv(size).decode()
        
        print(winner_message)
        #p.terminate()
        time.sleep(5)
        client = Client("Rick&Rick cause we are both genius")
        client.search_host()
    
    def play_sync(self):
        while True:  
            welcome_message = self.tcp.recv(size).decode()
            if "welcome" in welcome_message.lower():
                break
        print(welcome_message)
        
client = Client("Rick&Rick cause we are both genius")
client.search_host()
