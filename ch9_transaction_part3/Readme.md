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

## Transaction Validation 조건 추가

기본적으로, Transaction 을 통해 보내는 사람은 해당 Transaction을 서명하는 사람과 일치해야 한다. 따라서 validation_transaction 함수 ID를 확인하는 조건을 추가하였다.(sender_check 조건 참조)



```python
    @classmethod
    def validate_transaction(cls,transaction):
        header = transaction['header']
        body = transaction['body']

        if(body is None):
            return False
        if(header is None):
            return False
        
        ref_hash = binascii.a2b_base64(header['hash'].encode('ascii'))
        cur_hash = Blockchain.hash(json.dumps(body).encode(),False)
        pubKey = binascii.a2b_base64(header['publicKey'].encode('ascii'))
        public_key = RSA.importKey(pubKey)
        wallet_id = Blockchain.hash(public_key.exportKey('PEM'))        
        signature = header['signature']

        hash_check = ref_hash == cur_hash
        verify_result = public_key.verify(ref_hash,signature)
        sender_check = (wallet_id == body['sender']) #송금자는 서명자와 일치하여야 한다.

        result = (hash_check == True) and (verify_result == True) and (sender_check)
        return result
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

