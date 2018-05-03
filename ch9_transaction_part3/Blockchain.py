from time import time
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random
from pathlib import Path
import json
import requests
import binascii
from uuid import uuid4

class Blockchain(object):
    current_difficulty = 2
    key_file_name = "mykey.pem"

    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.peers = []
        self.peer_chains = []
        self.transaction_pool = []
        self.wallet = {}
        self.load_key()
        

        #Build genesis block
        self.new_block()

    @classmethod
    def hash(cls, data,hexdigest = True):
        if(hexdigest == True):
            return SHA256.new(data).hexdigest()
        else:
            return SHA256.new(data).digest()
            

    @classmethod
    def proof_of_work_validate(cls,block,difficulty):
        if difficulty == 0: return True
        target = ""
        for index in range(0,difficulty):
            target = target + "0"
            
        hash = Blockchain.hash(json.dumps(block).encode())
        return hash[:difficulty] == target

    @classmethod
    def validate_transaction(cls,transaction):
        header = transaction['header']
        body = transaction['body']

        if(body is None):
            return False
        if(header is None):
            return False
        
        ref_hash = binascii.a2b_base64(header['hash'].encode('ascii'))
        cur_hash = Blockchain.hash(json.dumps(body).encode(),False)
        pubKey = binascii.a2b_base64(header['publicKey'].encode('ascii'))
        public_key = RSA.importKey(pubKey)
        wallet_id = Blockchain.hash(public_key.exportKey('PEM'))        
        signature = header['signature']

        hash_check = ref_hash == cur_hash
        verify_result = public_key.verify(ref_hash,signature)
        id_check = (wallet_id == body['sender'])

        result = (hash_check == True) and (verify_result == True)
        return result

    @classmethod
    def validate_block(cls,block,difficulty):
        pof_validity = Blockchain.proof_of_work_validate(block,difficulty)
        transaction_validity = True
        for transaction in block['transactions']:
            valid = Blockchain.validate_transaction(transaction)
            if(valid == False):
                transaction_validity = False
        result = (pof_validity == True) and (transaction_validity == True)
        return result

    @classmethod
    def proof_of_work(cls,block,difficulty):
        nonce = 0
        while True:
            block['nonce'] = nonce
            if Blockchain.proof_of_work_validate(block,difficulty) == True : break
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

    def load_key(self):
        key_file = Path(self.key_file_name)
        if key_file.exists():
            # Open a new key file
            f = open(self.key_file_name,'rb')
            self.key = RSA.importKey(f.read())
            f.close()
        else:
            # Generate Pub/Priv Key
            random_generator = Random.new().read
            self.key = RSA.generate(1024,random_generator)
            
            # Export private key
            f = open(self.key_file_name,'wb')
            f.write(self.key.exportKey('PEM'))
            f.close()
        
        self.wallet['id'] = Blockchain.hash(self.key.publickey().exportKey('PEM'))


    def sign(self,hash):
        signature = self.key.sign(hash,'')
        return signature

    def new_transaction(self, values):
        new_transaction = {
            'body' : {
                'sender' : self.wallet['id'],
                'receiver' : values['receiver'],
                'amount' : values['amount']
            },
            'header' : {},
        }
        hash = Blockchain.hash(json.dumps(new_transaction['body']).encode(),False)
        signature = self.sign(hash)
        #new_transaction['header']['id'] = str(uuid4()).replace('-','')
        new_transaction['header']['hash'] = binascii.b2a_base64(hash).decode('ascii')
        new_transaction['header']['signature'] = signature
        new_transaction['header']['publicKey'] = binascii.b2a_base64(self.key.publickey().exportKey('PEM')).decode('ascii')
        self.current_transactions.append(new_transaction)
    

        

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

    def update_ledger(self):
        self.ledger = {}
        for block in self.chain:
            for transaction in block['transactions']:
                receiver =  transaction['body']['receiver']
                if receiver in self.ledger:
                    self.ledger[receiver] = self.ledger[receiver] + transaction['body']['amount']
                else:
                    self.ledger[receiver] = transaction['body']['amount']
        self.wallet['balance'] = self.ledger[self.wallet['id']]