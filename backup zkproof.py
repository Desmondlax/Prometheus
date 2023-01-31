from noknow.core import ZK, ZKSignature, ZKParameters, ZKData, ZKProof
from queue import Queue
from threading import Thread
import hashlib as hashlib

global q1, q2, q3, q4
x = "placeholder"

q1, q2, q3, q4 = Queue(), Queue(), Queue(), Queue()

def setToken(token):
    global tokenholder
    tokenholder = token

def infopassing(input:Queue, output: Queue, datapass: Queue, datacollect: Queue, zkproofstatement):
    
    datapass.put(zkproofstatement)
    
    return
    
def zkpassing(input:Queue, output: Queue, datapass: Queue, datacollect: Queue, token, zkproof):
    
    datapass.put(zkproof)
    datacollect.put(token)
    
    return

def client_obtain(input: Queue, output: Queue, datapass: Queue, datacollect: Queue):
    
    global client_zkp
    client_zkp = ZK.new(curve_name="secp256k1", hash_alg="sha256")

    #1. Make signature and sends it to the server
    userdata = datapass.get()
    
    signature = client_zkp.create_signature(userdata)
    output.put(signature.dump())

    #5. Server passes back the token
    token = input.get()

    return

def client_validate(input: Queue, output: Queue, datapass: Queue, datacollect: Queue, client_zkp : ZK, zkproof):
    
    #6. Proof is created, token is signed
    proof = client_zkp.sign(zkproof, tokenholder).dump()
    print(proof)

    #7. Send token and proof to the server
    output.put(proof)
    
    global x
    #10. Finish with action or something
    if input.get():
        x = True
        return x
    else:
        x = False
        return x

def server(input: Queue, output: Queue, datapass: Queue, datacollect: Queue):
    
    #2. server setup
    global server_zkp
    global client_signature
    
    server_zkp = ZK.new(curve_name="secp384r1", hash_alg="sha3_512")

    #3. Obtain signature from client
    sig = input.get()
    client_signature = ZKSignature.load(sig)
    client_zkp = ZK(client_signature.params)

    #4. Create signed token and send to client
    token = server_zkp.sign("SecurePassword", client_zkp.token())
    setToken(token)
    output.put(token.dump(separator=":"))
    
    return

def server_validate(input: Queue, output: Queue, datapass: Queue, datacollect: Queue):
    server_signature: ZKSignature = server_zkp.create_signature("SecurePassword")
    #8. Receive proof and token from client
    proof = ZKData.load(input.get())
    token = ZKData.load(proof.data, ":")

    #9. Signs token once verified 
    if not server_zkp.verify(token, server_signature):
        output.put(False)
    else:
        output.put(client_zkp.verify(proof, client_signature, data=token))
        return

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


def zkproofstartup():
    serverstart = Thread(target=server, args=(q2, q1, q3, q4))
    serverstart.start()

def zkproofvalidate(zkproof : str): 
    
    x = False
    clientvalidate = Thread(target=client_validate, args=(q1, q2, q3, q4, client_zkp, zkproof))
    x = clientvalidate.start()
    servervalidate = Thread(target=server_validate, args=(q2, q1, q3, q4))
    servervalidate.start()
    
    return x

def tokenpassing(zkproofstatement: str):
    tokenpass = Thread(target=infopassing, args=(q2, q1, q3, q4, zkproofstatement))
    tokenpass.start()
    tokenstatement = tokenpass.join()
    
    return tokenstatement

def serverrestart():
    serverstart = Thread(target=server, args=(q2, q1, q3, q4))
    serverstart.start()
    
def clientobtainrestart():
    clientstart = Thread(target=client_obtain, args=(q1, q2, q3, q4))
    clientstart.start()
    