import socket
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

HOST = '127.0.0.1'
PORT = 65432

# 1. Generate RSA-2048 private key for the server
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Extract the public key
public_key = private_key.public_key()

# Serialize the public key to bytes so it can be sent over the socket
public_key_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Server listening...")
    conn, addr = s.accept()
    
    with conn:
        print(f"Connected by {addr}")
        
        # 2. Send the public key to the client
        conn.sendall(public_key_bytes)
        
        # 3. Receive the encrypted session key from the client
        # RSA-2048 encryption yields a 256-byte ciphertext
        encrypted_session_key = conn.recv(256) 
        
        # 4. Decrypt the session key using the private key and RSA-OAEP
        session_key = private_key.decrypt(
            encrypted_session_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        print("Successfully decrypted the shared session key!")
        
        # --- Phase 2 logic resumes here ---
        # Initialize AESGCM(session_key) and start receiving messages