from time import time
from Crypto.Hash import SHA256
import json

class Blockchain(object):
	def __init__(self):
		self.current_transactions = None
		self.chain = []
		#Build genesis block
		self.new_block()
	@classmethod
	def hash(cls, data):
		return SHA256.new(data).hexdigest()

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
		self.chain.append(block)
		self.current_transaction = None
		return block

	def validate_chain(self,chain):
		chain_length = len(self.chain)
		for index in range(1,chain_length):
			prev_hash = Blockchain.hash(json.dumps(chain[index - 1]).encode())
			if chain[index]['prev_hash'] != prev_hash :
				return False
		return True

	def new_transaction(self, amount):
		self.current_transactions = {
			'amount' : amount
		}
	
