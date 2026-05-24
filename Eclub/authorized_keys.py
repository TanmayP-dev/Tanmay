# secure_server.py
import socket
import os
import json
import subprocess
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

HOST = '127.0.0.1'
PORT = 65432

# ... [Phase 3: Generate server RSA keys, listen, and receive the session key] ...
# Assume `session_key` was successfully decrypted from Phase 3
# session_key = private_key.decrypt(...)

aesgcm = AESGCM(session_key)

with conn: # Inside your existing socket connection block
    print("Encrypted channel established.")
    
    # --- PHASE 4: Client Authentication ---
    challenge = os.urandom(32)
    
    # Encrypt and send challenge
    nonce = os.urandom(12)
    enc_challenge = aesgcm.encrypt(nonce, challenge, associated_data=None)
    conn.sendall(nonce + enc_challenge) # Prepend nonce so client can read it
    
    # Receive encrypted signature
    resp = conn.recv(1024)
    resp_nonce = resp[:12] # First 12 bytes are the nonce
    enc_sig = resp[12:]
    signature = aesgcm.decrypt(resp_nonce, enc_sig, associated_data=None)
    
    # Verify Signature against authorized_keys.json
    with open("authorized_keys.json", "r") as f:
        authorized_keys = json.load(f)
        
    client_pub_pem = authorized_keys.get("client_1")
    client_pub_key = serialization.load_pem_public_key(client_pub_pem.encode())
    
    try:
        client_pub_key.verify(
            signature,
            challenge,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Client authenticated successfully!")
    except Exception:
        print("Authentication failed. Closing connection.")
        conn.close()
        exit() # Halt execution

    # --- PHASE 5: Remote Shell ---
    print("Starting remote shell...")
    while True:
        cmd_data = conn.recv(4096)
        if not cmd_data:
            break
            
        cmd_nonce = cmd_data[:12]
        enc_cmd = cmd_data[12:]
        command = aesgcm.decrypt(cmd_nonce, enc_cmd, associated_data=None).decode()
        
        print(f"Executing: {command}")
        
        # Run the command and capture output
        try:
            # shell=True allows commands like `ls` and `whoami` to resolve correctly
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout + result.stderr
            if not output:
                output = "[Command executed successfully with no output]"
        except Exception as e:
            output = f"Error executing command: {str(e)}"
            
        # Encrypt and send output back
        out_nonce = os.urandom(12)
        enc_output = aesgcm.encrypt(out_nonce, output.encode(), associated_data=None)
        conn.sendall(out_nonce + enc_output)