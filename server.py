import sys
import socket

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(("0.0.0.0", 1234))
socket.listen(5)

ip, port = socket.getsockname()
print(f"Server created: {ip}:{port}")
incomingSocket, incomingAddress = socket.accept()
print("Got connection from", incomingAddress)
while True:
    data = str(incomingSocket.recv(1024).decode())
    print(f"Received: {data}")

    if not data:
        break

    data = data.upper()
    incomingSocket.send(bytearray(str(data), encoding="utf-8"))
    print("Sent", data)


incomingSocket.close()
