# Chapter 10 : Transaction Part 4 -  Coinbase, UTXO



## 요약

Blockchain 의 Coin의 발행 역할을 하는 Coinbase Transaction과 Coin 소유권의 이동을 정의하기 위해 UTXO(Unspent Transaction Output)을 설계,구현하였다.



## Coinbase

### 개념

실제 화폐에서는 크게 두 가지 방식으로 화폐가 이동한다고 생각할 수 있다.

       	1. 물건 구매 등의 목적으로 화폐 소유권의 이동
   	2. 새로운 화폐의 발행

위 1번과 같은 방식이 이루어지기 위해서는 결국 화폐가 지속적으로 발생되어야(2번 방식) 화폐가 흐르고 사용 규모가 성장 할 수 있다.

가상화폐도 마찬가지로 Genesis Block에서부터 꾸준히 화폐가 생성되어야 지속적으로 Blockchain이 성장 가능하다. 이를 위해 Bitcoin에서는 매 Block 내에 Coinbase라는 특별한 Transaction을 추가할 수 있도록 하였다.

[^https://bitcoin.org/en/glossary/coinbase-transaction]: Bitcoin Coinbase Transaction

Bitcoin의 Coinbase transacton은 각 Block의 첫 Transaction을 Coinbase Transaction으로 정해놓고 있다. 이 Transaction은 다음과 같은 특징을 가지고 있다.

 - 반드시 블록을 생성한 사람이 서명한 Transaction이다.
 - 블록 내 첫 번째 Transaction이다.
 - Input Transaction이 UTXO일 필요가 없다.
    - Input Transaction으로 어느 값이 들어오든 상관 없다.

Coinbase의 역할은 새로운 Coin을 발행하는 것이다. 즉 사용자 간 거래를 기술하는 것이 아니라 매 Block 생성 시 화폐를 발행함으로써 Blockchain Coin의 총량을 증가시는 역할을 한다. 

추가로, Bitcoin에서는 Coinbase에서 생성되는 Bitocoin의 양이 일정하나, 반감기를 가지기 때문에 반감기가 지나면 Coinbase에서 생성되는 Bitcoin의 양이 줄어든다. 이 때문에 생성되는 Bitcoin의 총량은 정해져 있다.

### 설계

이번 예제에서는 다음과 같이 Bitcoin의 그것과 비슷하게 Coinbase를 설계해 보았다. 

- 매 Block의 첫 Transaction은 Coinbase로 정한다.
- Coinbase 의 입력은 어느 값이든 상관없다.
- Coinbase 의 출력 Transaction은 다음과 같다.
  - 소유자 : Block 을 생성한 사람
  - Amount : 100 (임의의 값)

Bitcoin의 반감기와 같은 개념은 여기서는 도입하지 않는다.

### 구현

#### Transaction 생성 함수 변경

기존 new_transaction 생성 함수에 *coinbase*라는 파라메터를 추가하였다. 이 파라메터가 True인 상태로 호출되면 Coinbase 생성을 위해 새로 만들어지는 Transaction은 current_transaction의 끝이 아닌 처음에 추가된다.

```python
    # new_transaction 메서드에 coinbase Parameter 추가
    # True : Coinbase Transaction 생성
    # False (Default) : 일반 Transaction 생성
    def new_transaction(self, values, coinbase = False):
		#생략
        if coinbase == False: # For normal transactions
            self.current_transactions.append(new_transaction)
        else:   # For coinbase (the first transaction in a block)
            self.current_transactions.insert(0,new_transaction)
```

#### Block 생성 함수 변경

블럭 생성 시 Coinbase Transaction을 추가 후 Proof of work 작업을 수행하도록 코드 추가

```python
    def new_block(self):
        # Coinbase Transaction
        values = {}
        values['receiver'] = self.wallet['id']
        values['amount'] = self.coinbase_amount #coinbase_amount : 100
        self.new_transaction(values,coinbase = True)        
        # 이하 생략

```



## UTXO

### 개념

#### TXID / TXIN / TXOUT

Coinbase 를 제외한 일반 Transaction을 올바르게 생성하려면 Transaction 내에 재사용되는 Coin이 존재해서는 안 되기 때문에 사용하고자 하는 Coin의 사용 여부를 알 필요가 있다. 그리고 Coin의 사용 여부를 알기 위해서는 해당 Coin의 사용 기록을 알 수 있어야 한다.  이를 위해 Bitcoin에서는 하나의 Transaction이 가지고 있는 정보를 크게 다음과 같이 나누었다.

 * TXID (Transaction ID) : Transaction 별 고유 번호
 * TXIN (Transaction Input) : 새 Transaction의 입력값
 * TXOUT (Transaction Output) : 새 Transaction의 출력값

TXID는 이후에 생성되는 Transaction들이 자기 자신을 참조할 수 있도록 만들어진 ID이다. TXIN과 TXOUT은 각각 하나의 Transaction에서 사용되어지는 Coin과 (TXIN) 그 결과로 소유권이 이전되는 Coin(TXOUT)을 의미한다. Bitcoin에서는 하나의 Transaction 내에 TXIN과 TXOUT을 각각 한 개 이상 포함할 수 있다.  따라서 TXOUT을 통해 소비되어지는 Coin의 양은 TXIN의 보다 클 수 없다. 

Bitcoin에서의 Transaction을 생성할 때 이 Transaction의 TXIN은 이전 Transaction에서 발생한 TXOUT을 참조한다. 이 TXOUT은 그 다음 Transaction의 TXIN으로서 사용되어지는 방식으로 Coin의 소유권이 이전된다.

#### UTXO

UTXO(Unspend Transaction Out)는 참조하고 있는 TXIN이 없는 TXOUT으로, 아직 사용하지 않았기 대문에 새 Transaction의 TXIN으로 사용 가능한 TXOUT을 의미한다. 따라서 Transaction이 유효하려면 TXIN이 참조하고 있는 모든 TXOUT은 UTXO이어야 한다.



### 설계

#### Transaction 구조 변경

- Transaction 구조는 다음과 같이 변경된다
  - TXID
  - TXIN 의 배열
  - TXOUT의 배열
- TXOUT은 다음과 (TXID,배열 Index)로 구분된다. 즉 TXIN은 (TXID,배열 Index)의 배열이다.
- TXOUT은 다음과 같은 구조를 가진다.
  - Amount : 이동하는 Coin의 양
  - Receive : 소유권이 이전되는 새 사용자의 Wallet ID

#### Transaction Validation 조건

하나의 Transaction은 다음과 같은 조건이 만족될 때 유효하다.

* TXID가 중복되지 않는다.
* SUM(TXIN.Amount) == SUM(TXOUT.Amount)
* Transaction 서명 Wallet ID == (모든 TXIN의 Receiver)
* Transaction 서명이 유효

#### Shared Ledger 구조 변경

현재까지 설계된 Ledger는 단순히 각 사용자 ID 별 잔액만을 저장하고 있다. UTXO를 구분하기 위해서는 Ledger를 통해 특정 Transaction 이 이미 사용된 Transaction 인지 아닌지 구분 할 수 있어야 한다. 따라서 Ledger은 Transaction 의 Map(TXID,TX) 이 되도록 하였다. 정리하면, Transaction 과 Shared Ledger는 다음과 같은 자료구조를 가진다.

* Key : TXID
* Data : Transaction의 배열. Transaction 은 다음과 같은 자료구조를 가진다.
  * TXID
  * TXIN의 배열 : 각 TXIN은 다음과 같은 자료구조를 가진다.
    * 대상 Transaction 의 TXID
    * 대상 Transaction의 TXOUT의 배열 Index
  * TXOUT의 배열 : 각 TXOUT은 다음과 같은 자료구조를 가진다 
    * Receiver : 새로운 소유자 Wallet ID
    * Amount :  전달되는 양
    * Spent : 처음 생성 시에는 False이나, 이후 새 Transaction에 의해 Reference 될 시 True 로 변경된다.

### 구현

#### Transaction 생성 함수 변경

Transaction 의 구조가 다소 크게 바뀌었다. 이에 Transaction 생성 함수도 변경이 필요하다.

##### TXID 추가

Transaction 생성 시 다음과 같이 TXID가 부여되도록 하였다.

```python
new_transaction['header']['id'] = str(uuid4()).replace('-','')
```

##### TXIN, TXOUT 항목 추가

새로 정의한 Transaction의 형식으로 만들어지도록 Transaction의 구조를 재정의하였다. 기존에 사용된 'amount' 항목은 삭제하였다. 

```python
        new_transaction = {
            'body' : {
                'TXIN' : values['TXIN'],
                'TXOUT' : values['TXOUT'],
            },
            'header' : {},
        }
```



