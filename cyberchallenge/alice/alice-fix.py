"""
This file represents Alice
"""
from socket import socket, AF_INET, SOCK_STREAM
import subprocess, sys, os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from helpers import *
import time


NAME = "alice"


def nspk_authentication(sock, server_name):
    """(socket, str) -> None
    Performs authentication via Needham-Schroeder public-key protocol.

    :sock: connection to server
    :server_name: name of server
    """
    # get RSA key of Alice
    rsa_key = rsa.import_key("RsaKey.asc")

    # get public key of file transfer server
    subprocess.Popen([sys.executable, "../pks/pks.py", 
        "--host=" + str(PKS_HOST),
        "--port=" + str(PKS_ALICE_PORT),
        "--extract"])
    time.sleep(1)
    pks_address = (PKS_HOST, PKS_ALICE_PORT)
    server_pkey = ns.get_public_key(pks_address, server_name, NAME, rsa_key)
    server_pkey = rsa.import_key(server_pkey)

    # A -- {N_A, A}(PK_B) --> B
    #
    # DONE
    #

    # Lowe's fix: A <-- {N_A, N_B, B}(PK_A) -- B
    #
    # TODO
    
    # if server names do not match, it must be an attack
    # send RESP_DENIED
    #
    # TODO
    #

    # A <-- {N_A, N_B}(PK_A) -- B
    #
    # DONE
    #

    # check if Bob actually did recieve Alice's nonce
    #
    # DONE
    #

    #    A -- {N_B}(PK_B) --> B
    #
    #    DONE
    #

    #    check if RESP_VERIFIED from Bob
    #
    #    DONE
    #

if __name__ == "__main__":
    import getopt
    def usage():
        print ('Usage:    ' + os.path.basename(__file__) + ' options input_file')
        print ('Options:')
        print ('\t -s server_name, --server=server_name')
        sys.exit(2)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hs:", ["help", "server="])
        if not opts:
            raise getopt.GetoptError("Enter an option")
    except getopt.GetoptError as err:
        print(err)
        usage()

    # extract parameters
    server_name = None
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        elif opt in ("-s", "--server"):
            server_name = arg

    # check arguments
    if server_name is None:
        print('server name option is missing\n')
        usage()
    address = None
    if server_name == "bob":
        address = (BOB_HOST, BOB_PORT)
    elif server_name == "charlie":
        address = (CHARLIE_HOST, CHARLIE_PORT)
    else:
        print("Alice: " + server_name + "not a valid server!")
        sys.exit(3)

    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.connect(address)

        # go through NSPK authentication protocol
        nspk_authentication(sock, server_name)

    print("Alice: client shutting down...")
