import socket
import os
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HOST = '127.0.0.1'
PORT = 65432
SHARED_KEY = b"This_is_a_32_byte_shared_key_123"

# Note: The plaintext is now explicitly a byte string (b"...")
MESSAGE = b"Hello, this is a secret AES-GCM test!"

while True:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            
            # 1. Initialize AES-GCM and generate a secure 12-byte nonce
            aesgcm = AESGCM(SHARED_KEY)
            nonce = os.urandom(12)
            
            # 2. Encrypt the plaintext (this generates the ciphertext + auth tag)
            ciphertext = aesgcm.encrypt(nonce, MESSAGE, associated_data=None)
            
            # 3. Combine the nonce and ciphertext to send over the network
            payload = nonce + ciphertext
            s.sendall(payload)
            print("Encrypted payload sent successfully!")
            
            # 4. Receive and decrypt the server's response
            data = s.recv(1024)
            if data:
                resp_nonce = data[:12]
                resp_ciphertext = data[12:]
                decrypted_response = aesgcm.decrypt(resp_nonce, resp_ciphertext, associated_data=None)
                print(f"Server replied: {decrypted_response.decode('utf-8')}")
                
        time.sleep(4) # Wait before sending the next message
    except ConnectionRefusedError:
        print("Connection failed: Server is not running.")
        time.sleep(2)
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(2)