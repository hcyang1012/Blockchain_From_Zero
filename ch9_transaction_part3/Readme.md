# Chapter 8 : Transaction Part 2 - Wallet, Shared Ledger



## 요약

Blockchain으로 데이터(여기서는 Coin)을 주고 받기 위한 계좌역할을 하는 지갑(Wallet)을 구현하고, 사용자 간 거래의 최종 결과가 기록되어있는 장부(Ledger)에 대한 초기 설계를 하였다.



## Wallet

개인 사용자의 Wallet은 다음과 같은 구조를 가진다

* Wallet ID : HASH(PUIBLIC_KEY)
* Balance : 계좌 잔액

따라서 새 Trannsation 생성 시 Body에는 다음과 같은  정보가 추가된다.

* Sender : Wallet ID
* Receive : 받는 사람의 Wallet ID
* Amount : 송금액



```python
    def new_transaction(self, values):
        new_transaction = {
            'body' : {
                'sender' : self.wallet['id'],
                'receiver' : values['receiver'],
                'amount' : values['amount']
            },
            'header' : {},
        }
        #이후 생략
```

따라서 /transaction/new API의 Parameter도 다음과 같이 변경되었다.

```python
@app.route('/transaction/new', methods=['POST'])
def route_transaction_new():
	values = request.get_json()
	required = ['receiver','amount']
	if not all (k in values for k in required):
		return "Missing values",400

	blockchain.new_transaction(values)
	response = {'message' : 'New transaction has been updated.'}
	return jsonify(response),201
```

내 Wallet 상태를 확인하기 위해 다음과 같은 /wallet/info API도 추가되었다.

```python
@app.route('/wallet/info',methods=['GET'])
def route_wallet_info():
	response = {
		'message' : 'Wallet information',
		'wallet' : blockchain.wallet,
	}
	return jsonify(response),200
```



## Transaction 탐색

현재 유지하고 있는 Blockchain 내 Transaction을 읽어 Blockchian 내 모든 사용자의 ID 및 계좌 잔액을 최신화한다.

구현 및 개념 이해의 용이를 위해 각 Transaction마다 단순히 amount만큼 잔액이 증가만 하도록 구현하였다.

```python
    def update_ledger(self):
        self.ledger = {}
        for block in self.chain:
            for transaction in block['transactions']:
                receiver =  transaction['body']['receiver']
                if receiver in self.ledger:
                    self.ledger[receiver] = self.ledger[receiver] + transaction['body']['amount']
                else:
                    self.ledger[receiver] = transaction['body']['amount']
        self.wallet['balance'] = self.ledger[self.wallet['id']]
```

이는 /ledger/info API로 호출 확인 가능

```python
@app.route('/ledger/info',methods=['GET'])
def route_ledger_info():
	blockchain.update_ledger()
	response = {
		'message' : 'My ledger',
		'ledger' : blockchain.ledger,
	}
	return jsonify(response),200
```

