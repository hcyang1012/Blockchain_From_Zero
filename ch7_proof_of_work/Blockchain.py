from time import time
from Crypto.Hash import SHA256
import json
import requests

class Blockchain(object):
    current_difficulty = 5
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.peers = []
        self.peer_chains = []
        self.transaction_pool = []
        #Build genesis block
        self.new_block()

    @classmethod
    def hash(cls, data):
        return SHA256.new(data).hexdigest()


    @classmethod
    def validate_block(cls,block,difficulty):
        if difficulty == 0: return True
        target = ""
        for index in range(0,difficulty):
            target = target + "0"
            
        hash = Blockchain.hash(json.dumps(block).encode())
        return hash[:difficulty] == target

    @classmethod
    def proof_of_work(cls,block,difficulty):
        nonce = 0
        while True:
            block['nonce'] = nonce
            if Blockchain.validate_block(block,difficulty) == True : break
            nonce = nonce + 1
        return nonce

    def new_block(self):
        if len(self.chain) > 0 :
            prev_hash = Blockchain.hash(json.dumps(self.chain[-1]).encode())
        else:
            prev_hash = 1
        block = {
                'index' : len(self.chain),
                'timestamp' : time(),
                'transactions' : self.current_transactions,
                'prev_hash' : prev_hash,
                }

        # ================== Proof of Work ==========================
        # Do proof of work to get the proper nonce
        nonce = Blockchain.proof_of_work(block,Blockchain.current_difficulty)  
        # Add nonce to the new block
        block['nonce'] = nonce
        # ===========================================================
        self.chain.append(block)
        self.current_transactions = []
        return block

    @classmethod
    def validate_chain_timesequence(cls,prev,curr):
        return prev['timestamp'] < curr['timestamp']

    @classmethod
    def validate_chain_hash(cls,prev,curr):
        calc_hash = Blockchain.hash(json.dumps(prev).encode())
        target_hash = curr['prev_hash']
        return calc_hash == target_hash

    @classmethod
    def validate_chain(cls,chain):
        chain_length = len(chain)
        for index in range(1,chain_length):
            test = {}
            prev = chain[index-1]
            curr = chain[index]
            test['timestamp'] = Blockchain.validate_chain_timesequence(prev,curr)
            test['hash'] = Blockchain.validate_chain_hash(prev,curr)
            test['block'] = Blockchain.validate_block(curr,Blockchain.current_difficulty) 
            test['result'] = (test['timestamp'] == True and test['hash'] == True and test['block'] == True)
            if test['result'] != True:
                test['curr'] = curr
                return test

        test = {}
        test['result'] = True
        return test
    def new_transaction(self, amount):
        self.current_transactions.append({
            'amount' : amount
            })
    def add_peer(self,peer):
        self.peers.append(peer)

    def collect(self):
        self.peer_chains = []
        newChain = False
        for peer in self.peers:
            peer_url =  "http://" + str(peer) + "/block/list"
            response = requests.get(peer_url)

        if response.status_code == 200:
            length = response.json()['length']
            chain = response.json()['list']
            validity = response.json()['validity']['result']
            if validity == True:
                self.peer_chains.append(chain)
                newChain = True
        return newChain

    def consensus(self):
        candidate_chain = self.chain
        for chain in self.peer_chains:
            if len(candidate_chain) < len(chain):
                candidate_chain = chain
        self.chain = candidate_chain
        self.peer_chains = []
        return self.chain

