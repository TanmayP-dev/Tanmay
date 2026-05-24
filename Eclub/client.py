import socket

HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    # This is the message you will look for in Wireshark
    message = "Hello, this is Tanmay"
    s.sendall(message.encode('utf-8'))
    data = s.recv(1024)

print(f"Server replied: {data.decode('utf-8')}")