class Blockchain(object):
	def __init__(self):
		self.current_transactions = None

	def new_transaction(self, amount):
		self.current_transactions = {
			'amount' : amount
		}
