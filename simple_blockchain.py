import hashlib
import time
import json

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions  # list of dicts
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            'index': self.index,
            'transactions': self.transactions,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty):
        # Simple Proof of Work: find hash starting with difficulty * "0"
        target = '0' * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4  # adjust for mining difficulty
        self.pending_transactions = []
        self.mining_reward = 50

    def create_genesis_block(self):
        return Block(0, [], time.time(), "0")

    def get_latest_block(self):
        return self.chain[-1]

    def mine_pending_transactions(self, miner_address):
        block = Block(len(self.chain), self.pending_transactions, time.time(), self.get_latest_block().hash)
        block.mine_block(self.difficulty)
        print(f"Block mined: {block.hash}")
        self.chain.append(block)

        # Reset pending transactions and add mining reward
        self.pending_transactions = [{
            'sender': "SYSTEM",
            'receiver': miner_address,
            'amount': self.mining_reward
        }]

    def create_transaction(self, sender, receiver, amount):
        self.pending_transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })

    def get_balance(self, address):
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx['sender'] == address:
                    balance -= tx['amount']
                if tx['receiver'] == address:
                    balance += tx['amount']
        # Also consider pending transactions to be fair
        for tx in self.pending_transactions:
            if tx['sender'] == address:
                balance -= tx['amount']
            if tx['receiver'] == address:
                balance += tx['amount']
        return balance

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                print("Current hash invalid")
                return False
            if current.previous_hash != previous.hash:
                print("Previous hash invalid")
                return False
        return True

# Example usage:
if __name__ == "__main__":
    my_coin = Blockchain()

    my_coin.create_transaction("Alice", "Bob", 100)
    my_coin.create_transaction("Bob", "Charlie", 50)

    print("Starting mining...")
    my_coin.mine_pending_transactions("Miner1")

    print(f"Balance of Miner1: {my_coin.get_balance('Miner1')}")
    print(f"Balance of Bob: {my_coin.get_balance('Bob')}")

    print("Starting mining again...")
    my_coin.mine_pending_transactions("Miner1")

    print(f"Balance of Miner1: {my_coin.get_balance('Miner1')}")
    print(f"Balance of Alice: {my_coin.get_balance('Alice')}")
    print(f"Balance of Bob: {my_coin.get_balance('Bob')}")
    print(f"Is chain valid? {my_coin.is_chain_valid()}")
