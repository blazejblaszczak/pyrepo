""" BASIC
import socket

# server setup
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 6789)) # bind to localhost and port 6789
server_socket.listen(5) # listen for incoming connections maximum of 5 only
print("Waiting for a connection...")
connection, address = server_socket.accept() # accept a connection

# receive data from client
data = connection.recv(1024)
print(f"Receiveed message: {data.decode()} from {address}")

# send a response to client
response = "Hello, client. Your message was received."
connection.send(response.encode())

# close the connection
connection.close()
"""

# V2

import socket
import threading
import sys


def handle_client(conn, addr):
    try:
        print(f"New connection from {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode()
            print(f"Received message from {addr}: {message}")
            if message.upper() == "QUIT":
                print(f"Quit command received. Client on port {addr} lost connection.")
                conn.send("Shutting down.".encode())
                conn.close()
                sys.exit(0) 
            response = "Your message was received"
            conn.send(response.encode())
    except Exception as e:
        print(f"An error occured with client {addr}: {e}")
    finally:
        conn.close()


def start_server():
    s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s_socket.bind(('localhost', 6789))
        s_socket.listen(5)
        print("Server is waiting for a connection...")
        while True:
            connection, address = s_socket.accept()
            client_thread = threading.Thread(target=handle_client, args=(connection, address))
            client_thread.start()
    except Exception as e:
        print(f"An error occured: {e}")
    finally:
        s_socket.close()


if __name__ == "__main__":
    start_server()
