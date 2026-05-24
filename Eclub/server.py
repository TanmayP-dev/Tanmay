import socket

HOST = '127.0.0.1' 
PORT = 65432        

print("Starting server...")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"SERVER IS ALIVE and listening on {HOST}:{PORT}...")
    print("Waiting for a client to connect...")
    
    while True:
        conn, addr = s.accept()
        with conn:
            print(f"\n--- SUCCESS! Client connected from {addr} ---")
            data = conn.recv(1024)
            if data:
                print(f"Received data: {data.decode('utf-8')}")
                conn.sendall(b"Message received by server")