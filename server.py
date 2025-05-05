import sys
import socket
import psycopg2

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(("0.0.0.0", 1234))
socket.listen(5)

ip, port = socket.getsockname()
print(f"Server created: {ip}:{port}")
incomingSocket, incomingAddress = socket.accept()
print("Got connection from", incomingAddress)
connection = psycopg2.connect(
    "postgresql://neondb_owner:npg_wbSvC7qAEGH3@ep-divine-meadow-a5w9f31z.us-east-2.aws.neon.tech/neondb?sslmode=require"
)

cursor = connection.cursor()



while True:
    data = str(incomingSocket.recv(1024).decode())
    print(f"Received: {data}")

    if not data:
        cursor.close()
        connection.close()
        break

    # data = data.upper()
    if data == 1:
        # method for querying for #1
        pass
    elif data == 2:
        # method for querying for #2
        pass
    else:
        #method for querying for #3
        pass


    # need functions for the queries 
    incomingSocket.send(bytearray(str(data), encoding="utf-8"))
    print("Sent", data)


incomingSocket.close()
