from flask import Flask,jsonify,request
from flaskrun import flaskrun
from Blockchain import Blockchain
from Attack import Blockchain_Attack


blockchain = Blockchain()

app = Flask(__name__)
# do some Flask setup here

@app.route('/',methods=['GET'])
def route_index():
	print("Hello,Blockchain!")
	return "Hello,Blockchain!"

@app.route('/transaction/list', methods=['GET'])
def route_transaction_list():
	response = {
		'transactions' : blockchain.current_transactions
	}
	return jsonify(response),200

@app.route('/transaction/new', methods=['POST'])
def route_transaction_new():
	values = request.get_json()
	required = ['amount']
	if not all (k in values for k in required):
		return "Missing values",400

	blockchain.new_transaction(values['amount'])
	response = {'message' : 'New transaction has been updated.'}
	return jsonify(response),201

@app.route('/block/new', methods=['GET'])
def route_block_new():
	new_block = blockchain.new_block()
	response = {
		'message' : 'New block generated',
		'index' : new_block['index'],
		'transactions' : new_block['transactions'],
		'prev_hash' : new_block['prev_hash'],
	}

	return jsonify(response),200
	
    
@app.route('/block/list', methods=['GET'])
def route_block_list():
	response = {
		'message' : 'Current blocks',
		'length' : len(blockchain.chain),
		'validity' : blockchain.validate_chain(blockchain.chain),
		'list' : blockchain.chain,
	}

	return jsonify(response),200

@app.route('/peers/add', methods=['POST'])
def route_peers_add():
	values = request.get_json()
	address = values['address']
	blockchain.add_peer(address)
	response = {'message' : 'A new peer has been added.'}
	return jsonify(response),201

@app.route('/peers/list', methods=['GET'])
def route_peers_list():
	response = {
		'message' : 'Peer list',
		'length' : len(blockchain.peers),
		'peers' : blockchain.peers,
	}

	return jsonify(response),200

@app.route('/peers/collect', methods=['GET'])
def route_peers_collect():
	newChain = blockchain.collect()
	response = {
		'message' : 'Collect chains from peers',
		'newChain' : newChain,
		'chains' : blockchain.peer_chains,
	}
	return jsonify(response),200


@app.route('/block/consensus', methods=['GET'])
def route_block_consensus():
	newChain = blockchain.consensus()
	response = {
		'message' : 'Consensus_result',
		'chain' : newChain,
	}
	return jsonify(response),200



@app.route('/attack/0_invalid_timestamp',methods=['GET'])
def route_attack0_invalid_timestamp():
	Blockchain_Attack.attack0_invalid_timestamp(blockchain);
	response = {
		'message' : 'I modified current blockchain. Try /block/list again!',
	}

	return jsonify(response),200

@app.route('/attack/1_invalid_hashchain',methods=['GET'])
def route_attack1_invalid_block():
	Blockchain_Attack.attack1_invalid_hashchain(blockchain);
	response = {
		'message' : 'I modified current blockchain. Try /block/list again!',
	}

	return jsonify(response),200

@app.route('/attack/2_attack2_replace_blockchain',methods=['GET'])
def route_attack2_replace_blockchain():
    Blockchain_Attack.attack2_replace_blockchain(blockchain)
    response = {
        'message' : 'Run consensus in other nodes',
    }

    return jsonify(response),200





flaskrun(app)

