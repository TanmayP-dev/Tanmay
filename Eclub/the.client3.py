import socket
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    # 1. Receive the server's public key (PEM format is typically ~450 bytes)
    public_key_bytes = s.recv(1024)
    
    # Load the bytes back into a usable public key object
    server_public_key = serialization.load_pem_public_key(public_key_bytes)
    
    # 2. Generate a random 32-byte session key for AES-GCM
    session_key = os.urandom(32)
    
    # 3. Encrypt the session key using the server's public key (RSA-OAEP)
    encrypted_session_key = server_public_key.encrypt(
        session_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    # 4. Send the encrypted session key to the server
    s.sendall(encrypted_session_key)
    print("Sent encrypted session key to the server.")
    
    # --- Phase 2 logic resumes here ---
    # Initialize AESGCM(session_key)
    # aesgcm = AESGCM(session_key)
    # nonce = os.urandom(12)
    # ... encrypt and send messages