from noknow.core import ZK, ZKSignature, ZKParameters, ZKData, ZKProof
from queue import Queue
from threading import Thread
import hashlib as hashlib

q1, q2 = Queue(), Queue()
x = False

def userdata(iq: Queue, oq: Queue, zkproof: str):
    oq.put(zkproof)
    iq.get(x)
    
    return x

def studentsignature(userdata):
    userdata2 = userdata
    new_nonce = 1
    check_nonce = False
    
    while not check_nonce:
        userdata3 = str(new_nonce) + userdata2
        encoded_userdata = userdata3.encode()
        hash = hashlib.sha256(encoded_userdata).hexdigest()

        if hash[:3] == "000":
            check_nonce = True
        else:
            new_nonce += 1
    
    zkproofstatement = hash     
    return zkproofstatement

def client(iq: Queue, oq: Queue):
    global x
    client_zk = ZK.new(curve_name="secp256k1", hash_alg="sha3_256")

    # Create signature and send to server
    zkproofstatement = iq.get()
    signature = client_zk.create_signature(zkproofstatement)
    oq.put(signature.dump())

    # Receive the token from the server
    token = iq.get()

    # Create a proof that signs the provided token and sends to server
    proof = client_zk.sign(zkproofstatement, token).dump()

    # Send the token and proof to the server
    oq.put(proof)

    # Wait for server response!
    if iq.get():
        x = True
        oq.put(x)
        return
    else:
        oq.put(x)
        return


def server(iq: Queue, oq: Queue):
    # Set up server component
    server_password = "SecretServerPassword"
    server_zk = ZK.new(curve_name="secp384r1", hash_alg="sha3_512")
    server_signature: ZKSignature = server_zk.create_signature("SecureServerPassword")

    # Load the received signature from the Client
    sig = iq.get()
    client_signature = ZKSignature.load(sig)
    client_zk = ZK(client_signature.params)

    # Create a signed token and send to the client
    token = server_zk.sign("SecureServerPassword", client_zk.token())
    oq.put(token.dump(separator=":"))

    # Get the token from the client
    proof = ZKData.load(iq.get())
    token = ZKData.load(proof.data, ":")

    # In this example, the server signs the token so it can be sure it has not been modified
    if not server_zk.verify(token, server_signature):
        oq.put(False)
        return
    else:
        oq.put(client_zk.verify(proof, client_signature, data=token))
        return


def zkstartup(zkproof):
    global x
    q1, q2 = Queue(), Queue()
    
    clientstart = Thread(target=client, args=(q1,q2))
    clientstart.start()
    serverstart = Thread(target=server, args=(q2,q1))
    serverstart.start()
    userdatastart = Thread(target=userdata, args=(q2,q1,zkproof))
    userdatastart.start()
    userdatastart.join()
    
    return x