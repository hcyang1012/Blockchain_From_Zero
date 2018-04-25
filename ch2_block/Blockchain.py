from time import time

class Blockchain(object):
	def __init__(self):
		self.current_transactions = None
		self.chain = []
		#Build genesis block
		self.new_block()

	def new_block(self):
		block = {
			'index' : len(self.chain),
			'timestamp' : time(),
			'transactions' : self.current_transactions,
		}
		self.chain.append(block)
		self.current_transactions = None
		return block

	def new_transaction(self, amount):
		self.current_transactions = {
			'amount' : amount
		}
