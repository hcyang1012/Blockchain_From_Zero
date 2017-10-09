import hashlib
import requests
import json

from time import time
from textwrap import dedent
from uuid import uuid4
from flask import Flask, jsonify, request
from urllib.parse import urlparse
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random
from pathlib import Path


key_file_name = "mykey.pem"
class Blockhain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.load_key()

        self.new_block(previous_hash = 1, proof = 100)

    def load_key(self):
        key_file = Path(key_file_name)
        if key_file.exists():
            # Open a new key file
            print("A key file is found. Load the key")
            f = open(key_file_name,'rb')
            private_key = RSA.importKey(f.read())
            f.close()
        else:
            # Generate Pub/Priv Key
            print("There is no key file. Create a new one")
            random_generator = Random.new().read
            private_key = RSA.generate(1024,random_generator)
    
                # Export private key
            f = open(key_file_name,'wb')
            f.write(private_key.exportKey('PEM'))
            f.close()
        self.private_key = private_key
        self.public_key = self.private_key.publickey()
        
        
    def register_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self,chain):
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print(str(last_block))
            print(str(block))
            print("\n-------------\n")
            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'],block['proof']):
                return False

            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            node_url = "http://" + str(node) + "/chain"
            response = requests.get(node_url)

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False


    def new_block(self,proof,previous_hash = None, validate = False):
        if validate == True:
            print(self.current_transactions)
            for transaction in self.current_transactions:
                if self.validate_transaction(transaction) != True:
                    return None
        block = {
            'index' : len(self.chain) + 1,
            'timestamp' : time(),
            'transactions': self.current_transactions,
            'proof' : proof,
            'previous_hash' : previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def validate_transaction(self,transaction):
       payload = transaction['payload']
       public_key = RSA.importKey(transaction['pubkey'].encode())
       signature = transaction['signature']

       hash = transaction['hash']
       calcHash = SHA256.new(json.dumps(payload).encode())
       
       if hash != calcHash.hexdigest():
           print("Hash error")
           return False


       validate = public_key.verify(calcHash.digest(),signature) 
       if validate == False:
           print("Invalid signature")
       return validate
        

    def new_transaction(self,sender,recipient,amount):
        payload = {
            'sender':sender,
            'recipient' : recipient,
            'amount' : amount,
        }
        payload_hash = SHA256.new(json.dumps(payload).encode());
        signature = self.private_key.sign(payload_hash.digest(),'')
        self.current_transactions.append({
            'payload':payload,
            'hash' : payload_hash.hexdigest(),
            'pubkey' : self.public_key.exportKey().decode(),
            # Valid signature
            'signature':signature,
            # Invalid signature
            #'signature':b'1234',
        })

        return self.last_block['index'] + 1

    def proof_of_work(self,last_proof):
        proof = 0
        while self.valid_proof(last_proof,proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof,proof):
        guess_str = str(last_proof) + str(proof)
        guess = guess_str.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        block_string = json.dumps(block,sort_keys = True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-','')
blockchain = Blockhain()

@app.route('/transactions/new',methods = ['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender','recipient','amount']
    if not all (k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'],values['recipient'],values['amount'])

    response = {'message' : "Transaction will be added to Block" + str(index)}
    return jsonify(response), 201

@app.route('/chain', methods = ['GET'])
def full_chain():
    response = {
        'chain' : blockchain.chain,
        'length' : len(blockchain.chain),
    }
    return jsonify(response),200

@app.route('/mine',methods = ['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        sender = "0",
        recipient = node_identifier,
        amount = 1,
    )

    block = blockchain.new_block(proof,validate = True)

    if block == None:
        return "Error : invalid transaction",400

    response = {
        'message' : "New Block Forged",
        'index' : block['index'],
        'transactions' : block['transactions'],
        'proof' : block['proof'],
        'previous_hash' : block['previous_hash'],
    }

    return jsonify(response), 200


@app.route('/nodes/register',methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error : Please supply a valid list of nodes",400

    for node in nodes:
        blockchain.register_node(node)

    resonse = {
        'message' : "New nodes have been added",
        'total_nodes' : list(blockchain.nodes),
    }

    return jsonify(resonse),201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message' : 'Our chain was replaced',
            'new_chain' : blockchain.chain
        }

    else:
        response = {
            'message' : 'Our chain is authoritative',
            'chain' : blockchain.chain
        }

    return jsonify(response),200



if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=5001)
