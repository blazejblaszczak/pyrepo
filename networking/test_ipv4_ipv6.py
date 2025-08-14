"""Client IPv6

import socket

HOST = '::1' # IPv6 loopback address | 127.0.0.1 in IPv4
PORT = 65432
with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as c_s:
    c_s.connect((HOST, PORT))
    c_s.sendall(b'Hello, IPv6 Server!')
    data = c_s.recv(1024)
    
print('Received', repr(data))
"""

"""Server IPv6

import socket

HOST = '::1' # IPv6 loopback address | 127.0.0.1 in IPv4
PORT = 65432
with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)
"""

# DUAL STACK CLIENT

import socket


HOST = 'localhost'       
PORT = 65432   

try:
    with socket.create_connection((HOST, PORT)) as s_ipv4:
        print("Connected via IPv4")
except ConnectionRefusedError:
    print("IPv4 Connection Failed")
  
# try to connect through IPv6
try:
    ipv6_info = socket.getaddrinfo(HOST, PORT, socket.AF_INET6)[0]
    # extract the IPv6 address
    address = ipv6_info[4][0]
    # create a connection
    with socket.create_connection((address, PORT)) as s_ipv6:
        print("Connected via IPv6")
except ConnectionRefusedError:
    print("IPv6 Connection Failed.")

# DUAL STACK SERVER

import socket


HOST = ''   # listen on all available interfaces       
PORT = 65432 


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_ipv4:
    # enable IPv4 and bind to the address and port
    s_ipv4.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s_ipv4.bind((HOST, PORT))
    s_ipv4.listen()
    print(f"IPv4 server listening on  {HOST}:{PORT}")
    with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as s_ipv6:
        s_ipv6.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s_ipv6.bind((HOST, PORT))
        s_ipv6.listen()
        print(f"IPv6 server listening on  {HOST}:{PORT}") 
        while True:
            # accept ipv4 connections
            conn_ipv4, addr_ipv4 = s_ipv4.accept()
            with conn_ipv4:
                print(f"Connected by IPv4 {addr_ipv4}")
                # handle ipv4 connection
            # accept ipv6 connections
            conn_ipv6, addr_ipv6 = s_ipv6.accept()
            with conn_ipv6:
                print(f"Connected by IPv6 {addr_ipv6}")
