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

    @classmethod
    def attack2_replace_blockchain(cls,blockchain):
        for repeat in range(0,20):
            blockchain.new_block()
