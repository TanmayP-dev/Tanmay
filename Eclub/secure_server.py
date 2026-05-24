import socket
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HOST = '127.0.0.1'
PORT = 65432

# AES-256 requires a 32-byte key. Both scripts MUST use this exact key.
SHARED_KEY = b"This_is_a_32_byte_shared_key_123"

print("Starting secure server...")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"SERVER IS ALIVE and listening on {HOST}:{PORT}...")
    
    while True:
        conn, addr = s.accept()
        with conn:
            print(f"\n--- SUCCESS! Client connected from {addr} ---")
            data = conn.recv(1024)
            if data:
                print(f"Raw encrypted bytes received: {len(data)} bytes")
                
                # 1. Extract the 12-byte nonce and the rest as ciphertext
                nonce = data[:12]
                ciphertext = data[12:]
                
                # 2. Initialize AES-GCM and decrypt
                aesgcm = AESGCM(SHARED_KEY)
                try:
                    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
                    print(f"Decrypted message: {plaintext.decode('utf-8')}")
                    
                    # 3. Securely encrypt a response back to the client
                    response_text = b"Message safely decrypted by server"
                    resp_nonce = os.urandom(12)
                    resp_ciphertext = aesgcm.encrypt(resp_nonce, response_text, associated_data=None)
                    conn.sendall(resp_nonce + resp_ciphertext)
                    
                except Exception as e:
                    print(f"Decryption failed (Tampering or wrong key): {e}")