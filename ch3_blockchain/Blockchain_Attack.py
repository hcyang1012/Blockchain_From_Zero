from Blockchain import Blockchain

class Blockchain_Attack:
	@classmethod	
	def attack0_invalid_block(cls,blockchain):
		if len(blockchain.chain) > 1 : 
			blockchain.chain[-2]['index'] = 'error index'
