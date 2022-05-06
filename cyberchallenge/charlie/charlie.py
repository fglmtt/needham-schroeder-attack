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

    # A -- {N_A, A}(PK_C) --> C
    #
    # TODO
    #

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
    #
    # TODO
    #

    # open connection with Bob's server
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect((BOB_HOST, BOB_PORT))
        print("Charlie: connected with bob")

        # C -- {N_A, A}(PK_B) --> B
        #
        # TODO
        #

        # C <-- {N_A, N_B}(PK_A) -- B
        #
        # TODO
        #

        # A <-- {N_A, N_B}(PK_A) -- C
        #
        # TODO
        #

        # A -- {N_B}(PK_C) --> C
        #
        # TODO
        #

        # C -- {N_B}(PK_B) --> B
        #
        # TODO
        #

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
