"""
This file represents Bob.
"""
from socket import socket, AF_INET, SOCK_STREAM
import subprocess, sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from helpers import *
import time


NAME = "bob"


def nspk_authentication(conn):
    """(socket, str) -> None
    Performs authentication via Needham-Schroeder public-key protocol.

    :conn: connection accepted from client
    """
    # get RSA key of Bob for decrypting
    rsa_key = rsa.import_key("RsaKey.asc")

    # A -- {N_A, A}(PK_B) --> B
    request = rsa.decrypt(rsa_key, conn.recv(1024))
    client_nonce, client_name = request.split(',')
    print("Bob: recieved nonce {} from client {}".format(client_nonce, client_name))

    # get client's public key
    subprocess.Popen([sys.executable, "../pks/pks.py", 
        "--host=" + str(PKS_HOST),
        "--port=" + str(PKS_BOB_PORT),
        "--extract"])
    time.sleep(1)
    pks_address = (PKS_HOST, PKS_BOB_PORT)
    client_pkey = ns.get_public_key(pks_address, client_name, NAME, rsa_key)
    client_pkey = rsa.import_key(client_pkey)

    # A <-- {N_A, N_B}(PK_A) -- B
    bob_nonce = ns.generate_nonce()
    response = "{},{}".format(client_nonce, bob_nonce)
    response = rsa.encrypt(client_pkey, response)
    conn.sendall(response)
    print("Bob: sent nonces {}, {} to {}".format(client_nonce, bob_nonce, client_name))

    # A -- {N_B}(PK_B) --> B
    request = rsa.decrypt(rsa_key, conn.recv(1024))
    bob_resp_nonce = int(request)
    print("Bob: recieved nonce {}".format(bob_resp_nonce))

    # check if client did actually recieve Bob's nonce
    if bob_resp_nonce == bob_nonce:
        print("Bob: connection with {} verified!".format(client_name))

	# confirm verified connection to the other side
        response = bytes(str(RESP_VERIFIED), "utf-8")
        conn.sendall(response)
    else:
        print("Bob: nonces {} and {} do not match!".format(bob_nonce, bob_resp_nonce))
        response = bytes(str(RESP_DENIED), "utf-8")
        conn.sendall(response)

if __name__ == "__main__":
    print("Bob: waiting to authenticate people...")
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.bind((BOB_HOST, BOB_PORT))
        sock.listen()
        conn, addr = sock.accept()
        with conn:
            print('Bob: connection from client with address', addr)
            nspk_authentication(conn)
