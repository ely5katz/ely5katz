from socket import *
import time
import struct
import getch
from multiprocessing import Process, Value
import psutil
# import keyboard
# CLIENT = gethostbyname(gethostname())
CLIENT = '20.100.102.12'
# broadcast port = udp port
BROADCAST_PORT = 13117
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
        self.udp.bind(('', BROADCAST_PORT))
        print(bcolors.OKCYAN+'Client started, listening for offer requests...')
        while True:
            try:
                message ,address = self.udp.recvfrom(size)
                #print(address)

        
                data = struct.unpack('ii', message)
                password = data[0]
                port = data[1]
                #print(password, port)
            except:
                continue
            if password == 5810:
                # We are about to play! let's connect to server.
                print(bcolors.WARNING+f"Received offer from {address[0]}, attempting to connect...")
                
                self.tcp.connect((address[0], port))
                self.tcp.send(f'{self.team_name}\n'.encode("ascii"))
                self.play()
           
            time.sleep(1)

    def play(self):
        p = Process(target= self.play_sync)
        p.start()
        winner_message = self.tcp.recv(size).decode()
        while 'answered' not in winner_message or 'draw' not in winner_message:
            winner_message = self.tcp.recv(size).decode()
            time.sleep(0.5)
        
        print(winner_message)
        p.terminate()
        time.sleep(5)
        client = Client("Pizza")
        client.search_host()
    
    def play_sync(self):
        while True:  
            welcome_message = self.tcp.recv(size).decode()
            if "welcome" in welcome_message.lower():
                break
        print(welcome_message)
        key_press = getch.getch()
        self.tcp.sendall(key_press.encode("ascii"))
        
client = Client("Pizza")
client.search_host()
