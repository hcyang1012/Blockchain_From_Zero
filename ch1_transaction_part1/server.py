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

    
flaskrun(app)

