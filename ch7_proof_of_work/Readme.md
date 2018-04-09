# Chapter 7 : Proof of work



## Proof of Work 관련 함수 추가

```python
    @classmethod
    def validate_block(cls,block,difficulty):
        if difficulty == 0: return True
        target = ""
        for index in range(0,difficulty):
            target = target + "0"
            
        hash = Blockchain.hash(json.dumps(block).encode())
        return hash[:difficulty] == target

    @classmethod
    def proof_of_work(cls,block,difficulty):
        nonce = 0
        while True:
            block['nonce'] = nonce
            if Blockchain.validate_block(block,difficulty) == True : break
            nonce = nonce + 1
        return nonce
        
```

### validate_block(block, difficulty)

block 이 정해진 difficulty를 만족하도록 proof of work 를 수행후 만들어졌는지 확인.

원래는 hash(block) < difficulty 를 만족하도록 설계하는 것이 정석이나, 
구현의 편의를 위해  difficulty를 *0의 개수(16진수 변환 시)* 로 정의하여 
16진수 hash값이 difficulty 개의 0으로 시작되는지 검증하도록 설계를 변형하였다.



### proof_of_work(block,difficulty)

nonce값을 0에서부터 증가시키머 
validate_block(block,difficulty) == True를 만족하는 nonce 를 찾은 후 
그 값을 block에 저장하는 함수.



## Blockchain Validation 기능 추가

Blockchain 의 각 블록을 검증 시 Proof of work 수행여부도 검증 항목에 추가



```python
    @classmethod
    def validate_chain(cls,chain):
        chain_length = len(chain)
        for index in range(1,chain_length):
            test = {}
            prev = chain[index-1]
            curr = chain[index]
            test['timestamp'] = Blockchain.validate_chain_timesequence(prev,curr)
            test['hash'] = Blockchain.validate_chain_hash(prev,curr)
            
            # Proof of work 검증 항목
            test['block'] = Blockchain.validate_block(curr,Blockchain.current_difficulty) 
            
            test['result'] = (test['timestamp'] == True and test['hash'] == True and test['block'] == True)
            if test['result'] != True:
                test['curr'] = curr
                return test

        test = {}
        test['result'] = True
        return test
```



## 블록 생성 시 Proo of Work 작업 수행

```python
    def new_block(self):
        if len(self.chain) > 0 :
            prev_hash = Blockchain.hash(json.dumps(self.chain[-1]).encode())
        else:
            prev_hash = 1
        block = {
                'index' : len(self.chain),
                'timestamp' : time(),
                'transactions' : self.current_transactions,
                'prev_hash' : prev_hash,
                }

        # ================== Proof of Work ==========================
        # Do proof of work to get the proper nonce
        nonce = Blockchain.proof_of_work(block,Blockchain.current_difficulty)  
        # Add nonce to the new block
        block['nonce'] = nonce
        # ===========================================================
        self.chain.append(block)
        self.current_transaction = []
        return block
```

