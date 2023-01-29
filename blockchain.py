"""
Genesis Block
{
    index : 0
    timestamp : current time
    transactions : "Genesis Block"
    nonce : 3
    previous_hash : "0"
}

This dict will be ran through a sha256 hash function to produce the hash, which will serve as the previous hash for the next block. Ex. hash = 342jkl5h34jkljklerg

{
    index : 1
    timestamp: current time
    transaction : "First Block"
    nonce : 34534
    previous_hash : "342jkl5h34jkljklerg"
}

hash = jk234h5jkl23hjk53hk5jl

{
    index : 2
    timestamp: current time
    transaction : "Second Block"
    nonce : 78378241
    previous_hash : "jk234h5jkl23hjk53hk5jl"
}

"""

import datetime as _datetime
import hashlib as _hashlib
import json as _json

class Blockchain:

    def __init__(self) -> None:
        self.chain = list()
        genesis_block = self._generate_block(transaction="Genesis block", nonce=1, prev_hash="0", index=1)
        self.chain.append(genesis_block)
    
    def _generate_block(self, transaction: str, nonce: int, prev_hash: str, index: int) -> dict:
        block = {
            "index": index,
            "timestamp": str(_datetime.datetime.now()),
            "transaction": transaction,
            "nonce": nonce,
            "prev_hash": prev_hash,
        }
        return block
    

    def _mine_block(self, transaction:str) -> dict:
        prev_block = self._get_prev_block()
        prev_nonce = prev_block["nonce"]
        index = len(self.chain) + 1
        nonce = self._proof_of_work(prev_nonce, index, transaction)
        prev_hash = self._hash_block(block=prev_block)
        block = self._generate_block(transaction=transaction, nonce=nonce, prev_hash=prev_hash, index=index)
        self.chain.append(block)
        
        return block

    def _hash_block(self, block: dict) -> str:
        encoded_block = _json.dumps(block, sort_keys=True).encode()
        
        return _hashlib.sha256(encoded_block).hexdigest()
    
    def _proof_of_work(self, prev_nonce: str, index: int, transaction: str) -> int:
        new_nonce = 1
        check_nonce = False

        while not check_nonce:
            to_compute = self._to_compute(new_nonce=new_nonce,prev_nonce=prev_nonce, index=index, transaction=transaction)
            hash = _hashlib.sha256(to_compute).hexdigest()

            if hash[:4] == "0000":
                check_nonce = True
            else:
                new_nonce += 1
                
        return new_nonce

    def _to_compute(self, new_nonce: int, prev_nonce: int, index: str, transaction: str) -> bytes:
        to_compute = str(new_nonce ** 2 - prev_nonce ** 2 + index) + transaction

        return to_compute.encode()
    
    def _get_prev_block(self) -> dict:
         return self.chain[-1]
    
    def _search_block(self, zkproof: str) ->dict:
        
        result = next(
            (item for item in self.chain if zkproof in item['transaction']),{}
        )
        
        blockindex = result.get('index')
        timestamp = result.get('timestamp')
        transaction = result.get('transaction')
        nonce = result.get('nonce')
        prev_hash = result.get('prev_hash')
        
        str(blockindex)
        str(timestamp)
        str(transaction)
        str(nonce)
        str(prev_hash)
        
        print(blockindex)
        print(timestamp)
        print(transaction)
        print(nonce)
        print(prev_hash)
        
        return blockindex, timestamp, transaction, nonce, prev_hash

    def _chain_validity(self) -> bool:
        prev_block = self.chain[0]
        block_index = 1

        while block_index < len(self.chain):
            block = self.chain[block_index]

            if block["prev_hash"] != self._hash_block(prev_block):
                return False
            
            prev_nonce = prev_block["nonce"]
            index, transaction, nonce = block["index"], block["transaction"], block["nonce"]

            hash_value = _hashlib.sha256(self._to_compute(new_nonce=nonce, prev_nonce=prev_nonce, index=index, transaction=transaction)).hexdigest()

            if hash_value[:4] != "0000":
                return False
            
            prev_block = block
            block_index += 1

        return True


            


