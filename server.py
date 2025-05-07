import sys
import socket
import psycopg2
import numpy as np
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
    cursor.execute("""SELECT payload->'DHT11 - moisture'
                   FROM "IOTdata_virtual" 
                   WHERE payload->>\'board_name\' = \'fridge_board_1\'
                   AND "time" >= NOW() - INTERVAL \'3 hours\'""")
    
    rows = cursor.fetchall()
    print(rows)
    connection.close()

    moisture_data = []
    for row in rows:
        moisture = float(row[0])
        moisture_data.append(moisture)
    
    moisture_average = np.average(moisture_data)

    print(moisture_average)
    return f'Average moisture (%RH) in your fridge in the last 3 hours is: {moisture_average}'

def option_2():
    return {"You have chosen option 2"}

def option_3():
    # connect to server first 
    connection = psycopg2.connect( "postgresql://neondb_owner:npg_wbSvC7qAEGH3@ep-divine-meadow-a5w9f31z.us-east-2.aws.neon.tech/neondb?sslmode=require")
    print("Connecting to database...")
    cursor = connection.cursor()

    # initiate variables
    fridge01 = 0.0
    fridge02 = 0.0
    dishwasher = 0.0
    count01 = 0
    count02 = 0
    count03 = 0

    # query for fridge 01
    cursor.execute(" SELECT payload->'ACS712 - Ammeter' " \
                    "FROM \"IOTdata_virtual\" " \
                    "WHERE payload->>'board_name' = 'fridge_board_1' " \
                    "AND \"time\" >= NOW() - INTERVAL '3 hours'")
    
    fridge01rows = cursor.fetchall()
    for row in fridge01rows:
        fridge01 += float(row[0])
        count01 += 1
    fridge01 = convert_to_kwh(count01, fridge01)

    # query for fridge02
    cursor.execute("SELECT payload->'sensor 3 ce68cdd6-7ec8-4aa5-9801-b67484bbac62' " \
                    "FROM \"IOTdata_virtual\" " \
                    "WHERE payload->>'board_name' = 'board 1 ce68cdd6-7ec8-4aa5-9801-b67484bbac62' " \
                    "AND \"time\" >= NOW() - INTERVAL '3 hours'")
    
    fridge02rows = cursor.fetchall()
    for row in fridge02rows:
        fridge02 += float(row[0])
        count02 += 1
    fridge02 = convert_to_kwh(count02, fridge02)

    # query for dishwasher
    cursor.execute("SELECT payload->'ACS712 - Ammeter_Dishwasher' " \
                    "FROM \"IOTdata_virtual\" " \
                    "WHERE payload->>'board_name' = 'dishwasher_board' " \
                    "AND \"time\" >= NOW() - INTERVAL '3 hours'")
    dishwasherRows = cursor.fetchall()
    for row in dishwasherRows:
        dishwasher += float(row[0])
        count03 += 1
    dishwasher = convert_to_kwh(count03, dishwasher)
    
    connection.close()

    # compare results, find greatest value
    list01 = [fridge01, fridge02, dishwasher]
    maxNum = 0.0
    index = 0
    for i in list01:
        if i > maxNum:
            maxNum = i
            index += 1
    devices= ["Fridge 01", "Fridge 02", "Dishwasher"]

    return f"{devices[index]} had the highest energy consumption: {maxNum} kWh"

def convert_to_kwh(count, total):
    average = total / count
    kwh_reading = round((120 * average * (count / 60)) / 1000, 1)
    return kwh_reading

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
        results = option_3()
    
    else:
        print("Wrong query option")

    # need functions for the queries 
    incomingSocket.send(bytearray(str(results), encoding="utf-8"))
    print("Sent", results)

incomingSocket.close()
