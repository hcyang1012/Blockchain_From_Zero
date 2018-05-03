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



### Key 생성 함수 추가

Blockchain 클래스에 RSA Public/Private Key 함수를 생성하는 멤버 함수를 추가하였다. 기존에 생성해 둔 키가 파일로 존재하면 파일에서 키를 읽어오고, 그렇지 않으면 새 키 쌍을 생성하여 사용한다.

```python
key_file_name = "mykey.pem"
	def load_key(self):
        key_file = Path(self.key_file_name)
        if key_file.exists():
            # Open a new key file
            f = open(self.key_file_name,'rb')
            self.key = RSA.importKey(f.read())
            f.close()
        else:
            # Generate Pub/Priv Key
            random_generator = Random.new().read
            self.key = RSA.generate(1024,random_generator)
            
            # Export private key
            f = open(self.key_file_name,'wb')
            f.write(self.key.exportKey('PEM'))
            f.close()
```



### Transaction 생성 함수 수정

```python
def new_transaction(self, amount):
    new_transaction = {
        'body' : {
            'amount' : amount
        },
        'header' : {},
    }
    hash = Blockchain.hash(json.dumps(new_transaction['body']).encode(),False)
    signature = self.sign(hash)
    new_transaction['header']['hash'] = binascii.b2a_base64(hash).decode('ascii')
    new_transaction['header']['signature'] = signature
    new_transaction['header']['publicKey'] = binascii.b2a_base64(self.key.publickey().exportKey('PEM')).decode('ascii')
    self.current_transactions.append(new_transaction)
```

#### Transaction 구조 변경 

amount 필드만 있던 기존 구조에서 Body, Header 로 나뉘는 구조로 변경

```python
    new_transaction = {
        'body' : {
            'amount' : amount
        },
        'header' : {},
    }
```

#### Header Field 구성

아래와 같은 Field들로 Header 구성

- Hash : Hash of body
- Signature : public key로 생성한 Hash의 디지털 서명
- Public Key :  서명 생성 시 사용한 Public Key

### Transaction Validation 함수 추가

아래 조건이 맞을 때 Transaction 하나의 유효성이 검증됨.

1. Hash[Body] = Header['hash']
2. Verify(Header['hash'], Header['Signature'],Header['PublicKey']) = True

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
        signature = header['signature']

        hash_check = ref_hash == cur_hash
        verify_result = public_key.verify(ref_hash,signature)

        result = (hash_check == True) and (verify_result == True)
        return result
```

