# secure_client.py
import socket
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HOST = '127.0.0.1'
PORT = 65432

# ... [Phase 3: Connect, receive server public key, generate & send session key] ...
# session_key = os.urandom(32)

aesgcm = AESGCM(session_key)

# Load the client's private key
with open("client_private.pem", "rb") as f:
    client_private_key = serialization.load_pem_private_key(f.read(), password=None)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # (Connection logic goes here)
    
    # --- PHASE 4: Authentication ---
    # Receive encrypted challenge
    chal_data = s.recv(1024)
    chal_nonce = chal_data[:12]
    enc_challenge = chal_data[12:]
    challenge = aesgcm.decrypt(chal_nonce, enc_challenge, associated_data=None)
    
    # Sign the challenge with RSA-PSS
    signature = client_private_key.sign(
        challenge,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    # Encrypt and send the signature
    sig_nonce = os.urandom(12)
    enc_sig = aesgcm.encrypt(sig_nonce, signature, associated_data=None)
    s.sendall(sig_nonce + enc_sig)
    
    print("Authentication sent. Waiting for shell access...")
    
    # --- PHASE 5: Remote Shell Interface ---
    while True:
        command = input("ec-shell> ")
        if command.lower() in ['exit', 'quit']:
            break
            
        # Encrypt and send command
        cmd_nonce = os.urandom(12)
        enc_cmd = aesgcm.encrypt(cmd_nonce, command.encode(), associated_data=None)
        s.sendall(cmd_nonce + enc_cmd)
        
        # Receive and decrypt output
        out_data = s.recv(8192) # Larger buffer for command outputs
        out_nonce = out_data[:12]
        enc_out = out_data[12:]
        output = aesgcm.decrypt(out_nonce, enc_out, associated_data=None).decode()
        
        print(output)