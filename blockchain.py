import hashlib, time

class Block:
    def __init__(self, index, voter, candidate, prev_hash):
        self.index = index
        self.timestamp = time.time()
        self.voter = voter
        self.candidate = candidate
        self.prev_hash = prev_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        return hashlib.sha256(f"{self.index}{self.voter}{self.candidate}{self.prev_hash}{self.timestamp}".encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "Genesis", "None", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, voter, candidate):
        prev = self.get_latest_block()
        new_block = Block(len(self.chain), voter, candidate, prev.hash)
        self.chain.append(new_block)

    def count_votes(self):
        results = {}
        for block in self.chain[1:]:
            results[block.candidate] = results.get(block.candidate, 0) + 1
        return results
