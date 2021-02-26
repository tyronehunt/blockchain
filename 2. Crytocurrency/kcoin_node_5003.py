# Module 2 - Create a Cryptocurrency

# Import the libraries
import datetime
import hashlib
import json  
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse


# Part 1 - Building a Blockchain
class Blockchain:
    
    def __init__(self):
        # Initiate list of dictionaries (i.e. blockchain)
        self.chain = []
        # List of transactions (before they're added to block)
        self.transactions = []
        #Create genesis block - convention is initial hash = 0
        self.create_block(proof = 1, previous_hash = '0')
        #Create nodes
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1, 
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof, 
                 'previous_hash': previous_hash,
                 'transactions': self.transactions
                 }
        
        self.transactions = [] # empty transactions, once added to the block
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        """Find a number (new_proof), which when combined with the previous block's proof & hashed into hexidecimal
        satisfies the POW requirement. Return this 'solving' number (correct new proof)
        """
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        """ Create cryptographic hash (string) for block. """
        # Encode block into format expected by hashlib sha256 function
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        """ Checks all blocks are connected and that proofs are valid for their blocks."""
        previous_block = chain[0]
        block_index = 1
        # Loop through blocks
        while block_index < len(chain):
            block = chain[block_index]
            # Check 1 - the blocks are linked by the previous_hash value
            if block['previous_hash'] != self.hash(previous_block):
                return False
            # Check 2 - hash operation satisfies the POW conditions (0000)
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            # Next iteration
            previous_block = block 
            block_index += 1
        return True
    
    def add_transaction(self, sender, receiver, amount):
        """Add a transaction dictionary to the transactions list, 
         return the block index it will be written to"""
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
            
        previous_block = self.get_previous_block()
        return previous_block['index'] + 1
    
    def add_node(self, address):
        """Add node containing that address to set of nodes"""
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netlock)
            
    def replace_chain(self):
        """ Check if node is up to date (longest chain) and replace if not """
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain) # Until we scan the network, this node has longest chain
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain =  response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
    
    
# Part 2 - Mining the Blockchain
        
# Create a Wep App 
app = Flask(__name__)

# Creating an address for the node on Port 5000 (to start first node)
node_address = str(uuid4()).replace('-', '')

# Create instance of blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    """Take previous block (and it's proof), search for new_proof that solves POW requirement. 
    Create a new block on the blockchain."""
    # First find the proof
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    # Add block to blockchain
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = 'you', amount=1)
    block = blockchain.create_block(proof, previous_hash)
    # Display block
    response = {'message': 'Congratulations - you mined a block!', 
                'index': block['index'],
                'timestamp':block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions': block['transactions']
                }
    # Return response in json format
    return jsonify(response), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)
                }
    return jsonify(response), 200

# Check if blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'Blockchain is valid.'}
    else:
        response = {'message': 'Blockchain is NOT valid.'}
    return jsonify(response), 200 

# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'some elements of the transaction are missing', 400
    # index of block is returned from the add_transaction() method of blockchain
    index = blockchain.add_transaction(json['sender'], 
                                       json['receiver'], 
                                       json['amount'])
    response = {'message': f'This transaction will be added to Block {index}'}
    return jsonify(response), 201    


# Part 3 - Decentralising our Blockchain
# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes: 
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The KCoin Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The node had different chains, chain has been updated with longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'The chain is the longest available.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200 


# Run the app
app.run(host='0.0.0.0', port=5003)
    


        
