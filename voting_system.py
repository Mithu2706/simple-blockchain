import hashlib
import json
import time

class Block:
    def __init__(self, index, timestamp, votes, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.votes = votes  # list of vote dicts
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()
        
    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "votes": self.votes,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self):
        self.unconfirmed_votes = []
        self.chain = []
        self.create_genesis_block()
        
    def create_genesis_block(self):
        genesis_block = Block(0, time.time(), [], "0")
        self.chain.append(genesis_block)
        
    @property
    def last_block(self):
        return self.chain[-1]
    
    def add_vote(self, voter_id, candidate):
        vote = {"voter_id": voter_id, "candidate": candidate}
        self.unconfirmed_votes.append(vote)
        
    def add_block(self, block, proof):
        previous_hash = self.last_block.hash
        
        if previous_hash != block.previous_hash:
            return False
        
        if not self.is_valid_proof(block, proof):
            return False
        
        block.hash = proof
        self.chain.append(block)
        return True
    
    def proof_of_work(self, block, difficulty=2):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash
    
    def mine(self):
        if not self.unconfirmed_votes:
            return False
        
        last_block = self.last_block
        new_block = Block(index=last_block.index + 1,
                          timestamp=time.time(),
                          votes=self.unconfirmed_votes,
                          previous_hash=last_block.hash)
        
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_votes = []
        return new_block.index
    
    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * 2) and
                block_hash == block.compute_hash())
    
    def count_votes(self):
        tally = {}
        for block in self.chain[1:]:  # skip genesis
            for vote in block.votes:
                candidate = vote['candidate']
                tally[candidate] = tally.get(candidate, 0) + 1
        return tally

# Example usage:
blockchain = Blockchain()
blockchain.add_vote("voter1", "Alice")
blockchain.add_vote("voter2", "Bob")
blockchain.mine()

blockchain.add_vote("voter3", "Alice")
blockchain.mine()

print("Vote tally:", blockchain.count_votes())
