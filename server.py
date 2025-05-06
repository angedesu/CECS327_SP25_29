import sys
import socket
import psycopg2
import json

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(("127.0.0.1", 1234))
socket.listen(5)

ip, port = socket.getsockname()
print(f"Server created: {ip}:{port}")
incomingSocket, incomingAddress = socket.accept()
print("Got connection from", incomingAddress)

connection = psycopg2.connect(
    "postgresql://neondb_owner:npg_wbSvC7qAEGH3@ep-divine-meadow-a5w9f31z.us-east-2.aws.neon.tech/neondb?sslmode=require"
)
print("Connecting to database...")
cursor = connection.cursor()

def option_1():
    # connection to database
    cursor.execute('SELECT payload FROM "IOTdata_virtual" WHERE payload->>\'board_name\' = \'fridge_board_1\'AND "time" >= NOW() - INTERVAL \'3 hours\'')
    
    rows = cursor.fetchall()
    connection.close()

    numbers = []
    for row in rows:
        payload = json.loads(row[0])
        moisture = payload.get("DHT11 - moisture")
        if moisture:
            numbers.append(float(moisture))

    average = round(sum(numbers) / len(numbers), 2) 
    print(average)
    return {f'Average moisture (%RH) in your fridge in the last 3 hours is: {average}'}

def option_2():
    return {"You have chosen option 2"}

def option_3():
    return {"You have chosen option 3"}

while True:
    data = str(incomingSocket.recv(1024).decode())
    print(f"Received: {data}")

    '''if not data:
        cursor.close()
        connection.close()
        break'''

    
    if data == "1":
        print("Received option 1")
        results = option_1()
        
        
    elif data == "2":
        print("Received option 2")
        # method for querying for #2
        results = 2

    elif data == "3":
        print("Received option 3")
        #method for querying for #3
        results = 3
    
    else:
        print("Wrong query option")
    



    # need functions for the queries 
    incomingSocket.send(bytearray(str(results), encoding="utf-8"))
    print("Sent", results)

incomingSocket.close()


