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
    # Get user query selection
    try: 
        user_query = int(input(("\nEnter 1, 2, or 3 to choose between these three query options:\n"
                        "1. What is the average moisture inside my kitchen fridge in the past three hours?\n"
                        "2. What is the average water consumption per cycle in my smart dishwasher?\n"
                        "3. Which device consumed more electricity among my three IoT devices (two refridgerators and a dishwasher)?")))
    except:
        print("Sorry, this query cannot be processed. Please try inputing 1, 2, or 3.")
        continue

    # Process user query
    if user_query == 1:
        print("Query 1 selected")
        # Do stuff here
    elif user_query == 2:
        print("Query 2 selected")
    elif user_query == 3:
        print("Query 3 selected")
    else: 
        print("Sorry, this query cannot be processed. Please try inputing 1, 2, or 3.")

    # Send query selection to server
    socket.send(bytearray(user_query, encoding='utf-8'))
    response = socket.recv(1024).decode('utf-8')
    print("Response:", response)

socket.close()

