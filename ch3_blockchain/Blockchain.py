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
		self.current_transactions = None
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
			test['result'] = (test['timestamp'] == True and test['hash'] == True)
			if test['result'] != True:
				test['curr'] = curr
				return test
			
		test = {}
		test['result'] = True
		return test

	def new_transaction(self, amount):
		self.current_transactions = {
			'amount' : amount
		}
	
