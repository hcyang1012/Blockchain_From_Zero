from flask import Flask,jsonify,request
from flaskrun import flaskrun
from Blockchain import Blockchain


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
	}

	return jsonify(response),200
	
    
@app.route('/block/list', methods=['GET'])
def route_block_list():
	response = {
		'message' : 'Current blocks',
		'length' : len(blockchain.chain),
		'list' : blockchain.chain,
	}

	return jsonify(response),200

flaskrun(app)

