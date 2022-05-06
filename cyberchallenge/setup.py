from helpers import *
from socket import socket, AF_INET, SOCK_STREAM
import sys
import subprocess
import time


def main():
    # generate RSA keys
    alice_key = rsa.generate_key()
    print("RSA key successfully generated for Alice")
    bob_key = rsa.generate_key()
    print("RSA key successfully generated for Bob")
    charlie_key = rsa.generate_key()
    print("RSA key successfully generated for Charlie")

    # save private keys to respective directories
    rsa.export_key(alice_key, "alice/RsaKey.asc")
    print("RSA key successfully saved for Alice")
    rsa.export_key(bob_key, "bob/RsaKey.asc")
    print("RSA key successfully saved for Bob")
    rsa.export_key(charlie_key, "charlie/RsaKey.asc")
    print("RSA key successfully saved for Charlie")

    # start up public key server
    subprocess.Popen([sys.executable, "pks/pks.py",
        "--host=" + str(PKS_HOST),
        "--port=" + str(PKS_SETUP_PORT),
        "--setup"])
    time.sleep(1)

    # get public keys to send to public key server to save
    alice_pk = rsa.export_public_key(alice_key)
    bob_pk = rsa.export_public_key(bob_key)
    charlie_pk = rsa.export_public_key(charlie_key)

    # begin communications with PKS
    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect((PKS_HOST, PKS_SETUP_PORT))
        # send Alice's public key
        sock.sendall(b'alice$' + alice_pk)
        resp = sock.recv(1024)
        print('Received', resp)
        # send Bob's public key
        sock.sendall(b'bob$' + bob_pk)
        resp = sock.recv(1024)
        print('Received', resp)
        # send Mallory's public key
        sock.sendall(b'charlie$' + charlie_pk)
        resp = sock.recv(1024)
        print('Received', resp)


if __name__ == "__main__":
    main()
