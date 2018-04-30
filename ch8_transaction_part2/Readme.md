# Chapter 8 : Transaction Part 2 - Transaction Signing



## 요약

Block 내 Transaction의 Validity 중 Non-repudiation(부인 방지)를 구현하기 위해 Transaction Signing 기능을 추가하였다. 



## Signing 관련 함수 추가

### Hash 함수 변경

Sign() 함수 호출을 위해 hash함수에 Hash값을 String 뿐 아니라 Byte String으로도 생성할 수 있도록 기능 추가. 



```python
def hash(cls, data,hexdigest = True):
    if(hexdigest == True):
        return SHA256.new(data).hexdigest()
    else:
        return SHA256.new(data).digest()
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



### Block Validation 함수 동작 변경

Chapter 7에서 Proof of work 검증기능을 수행하던 validate_block() 함수에 Transaction Validation 기능을 추가.



```python
    @classmethod
    def validate_block(cls,block,difficulty):
        pof_validity = Blockchain.proof_of_work_validate(block,difficulty)
        transaction_validity = True
        for transaction in block['transactions']:
            valid = Blockchain.validate_transaction(transaction)
            if(valid == False):
                transaction_validity = False
        result = (pof_validity == True) and (transaction_validity == True)
        return result
```



## 기타

### Proof of Work 함수 동작 변경

Chapter 7에서 proof_of_work 함수가 호출하던 Block Validation 함수가 Transaction Validation 기능까지 추가되었기 때문에 proof_of_work 함수에서는 기존 validate_block() 함수 대신 Proof of work 작업 검증만을 수행하는 proof_of_work_validate() 함수를 호출하도록 동작 변경



```python
    @classmethod
    def proof_of_work(cls,block,difficulty):
        nonce = 0
        while True:
            block['nonce'] = nonce
            if Blockchain.proof_of_work_validate(block,difficulty) == True : break
            nonce = nonce + 1
        return nonce
```



## References

1. http://pycryptodome.readthedocs.io/en/latest/src/public_key/rsa.html