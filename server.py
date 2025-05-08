import sys
import socket
import psycopg2
import numpy as np
import datetime

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
    # query 
    cursor.execute("""SELECT payload->'DHT11 - moisture'
                   FROM "IOTdata_virtual" 
                   WHERE payload->>\'board_name\' = \'fridge_board_1\'
                   AND "time" >= NOW() - INTERVAL \'3 hours\'""")
    
    results = cursor.fetchall()
    

    moisture_data = []
    for row in results:
        moisture = float(row[0])
        moisture_data.append(moisture)
    
    moisture_average = np.average(moisture_data)

    print(moisture_average)
    return f'Average moisture (%RH) in your fridge in the last 3 hours is: {moisture_average:.2f}'

def option_2():
    # Query dishwasher water consumption data
    cursor.execute("""SELECT "time", payload->'Capacitive Liquid Level Sensor - WaterConsumption'
                      FROM "IOTdata_virtual"
                      WHERE payload->>'board_name' = 'dishwasher_board'
                      ORDER BY "time" ASC""")
    
    results = cursor.fetchall()
    print(len(results))

    # Process the query result into 2-hour cycles
    cycles = {} # Dictionary to hold the cycles data
    
    first_timestamp = results[0][0]
    last_timestamp = results[-1][0]

    print("First timestamp:", first_timestamp)
    print("Last timestamp:", last_timestamp)
    print("Duration (hours):", (last_timestamp - first_timestamp).total_seconds() / 3600)

    for timestamp, water_consumption in results:
        time_difference = last_timestamp - timestamp
        hours_back = int(time_difference.total_seconds() // 3600) 
        cycle_index = hours_back // 3

        # Define the start/end time for this cycle
        cycle_end = last_timestamp - datetime.timedelta(hours=cycle_index * 3)
        cycle_start = cycle_end - datetime.timedelta(hours=2) # There will be a 1 hour gap between each cycle

        key = (cycle_start, cycle_end)

        # Add the cycle to dictionary if it doesn't exist
        if key not in cycles:
            cycles[key] = []
        
        cycles[key].append(float(water_consumption))
    
    print(len(cycles))
    
    # Calculate average water consumption for each cycle
    per_cycle_average = []
    for values in cycles.values():
        avg = np.average(values)
        per_cycle_average.append(avg)
    
    # Calculate average of those averages
    avg_per_cycle = np.average(per_cycle_average)
    
    
    return f"Average water consumption per cycle in your dishwasher: {avg_per_cycle:.2f}"


def option_3():
    # initiate variables
    fridge01 = 0.0
    fridge02 = 0.0
    dishwasher = 0.0
    count01 = 0
    count02 = 0
    count03 = 0

    # query for fridge01
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
    
    if data == "1":
        results = option_1()
        
    elif data == "2":
        results = option_2()

    elif data == "3":
        results = option_3()
    
    else:
        cursor.close()
        connection.close()
        break

    # need functions for the queries 
    incomingSocket.send(bytearray(str(results), encoding="utf-8"))
    print("Sent", results)

incomingSocket.close()
