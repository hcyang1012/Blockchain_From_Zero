from Blockchain import Blockchain
from time import time

class Blockchain_Attack:
	@classmethod	
	def attack0_invalid_timestamp(cls,blockchain):
		if len(blockchain.chain) > 1 : 
			blockchain.chain[-2]['timestamp'] = time()

	@classmethod	
	def attack1_invalid_hashchain(cls,blockchain):
		if len(blockchain.chain) > 1 : 
			blockchain.chain[-2]['index'] = 'error index'
