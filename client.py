import sys
import socket

ip = input("Input IP address: ")
port = int(input("Input port number: "))

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    socket.connect((ip, port))
except:
    print("Incorrect IP address or Port Number. Goodbye.")
    sys.exit()

while True:
    message = input("Input message: ")
    socket.send(bytearray(str(message), encoding='utf-8'))
    response = socket.recv(1024).decode('utf-8')
    print("Response:", response)

socket.close()

