import binascii

from flask import Flask, render_template, jsonify, request
from time import time
from flask_cors import CORS
from collections import OrderedDict
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from uuid import uuid4
import json
import hashlib


MINING_SENDER = "The Blockchain"
MINING_REWARD = 1
MINNING_DIFFICULTY = 2

class Blockchain:
    def __init__(self):
        self.transactions = []
        self.node_id = str(uuid4()).replace('-','')
        self.chain = []
        self.create_block(0, '00') #create genesis block

    def create_block(self, nonce, previous_hash): # add block of transactions to block chain
        block = {
            'block_number': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.transactions,
            'nonce': nonce,
            'previous_hash': previous_hash
        }
        self.transactions = [] #reset current list of transactions
        self.chain.append(block)
        return block

    def verify_transaction_signature(self, sender_public_key, signature, transaction):
        public_key = RSA.importKey(binascii.unhexlify(sender_public_key))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA.new(str(transaction).encode('utf8'))
        try:
            verifier.verify(h, binascii.unhexlify(signature)) #returns true if h matches the senders public key
            return True
        except ValueError:
            return False


    def valid_proof(self, transactions, last_hash, nonce, difficulty = MINNING_DIFFICULTY):#difficulty = number of 0s we are looking for at start of hash
        guess = (str(transactions) + str(last_hash) + str(nonce)).encode('utf8')
        h = hashlib.new('sha256')
        h.update(guess)
        guess_hash = h.hexdigest() #hash of 3 variables from guess
        return guess_hash[:difficulty] == '0'* difficulty #determine if hash is valid proof, check for proper number of 0s, get first {difficulty} numbers of hash
        #true if valid proof




    def proof_of_word(self): #objective is to find a nonce that meets criteria (target), hash w/ specific amount of 0s

        nonce = 0 #will be increamented by 1 until a hash is produced that meets criteria

        last_block = self.chain[-1]
        last_hash = self.hash(last_block)

        while self.valid_proof(self.transactions, last_hash, nonce) is False:
            nonce += 1

        return nonce

    def hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode('utf8') #ensure the dictionary is ordered, avoid inconsistent hashes
        h = hashlib.new('sha256')
        h.update(block_string)
        return h.hexdigest()


    def submit_transaction(self, sender_public_key, recipient_public_key, signature, amount):


        transaction = OrderedDict({
            'sender_public_key': sender_public_key,
            'recipient_public_key': recipient_public_key,
            'amount':amount
        })




        if sender_public_key == MINING_SENDER: #reward for mining a block
            self.transactions.append(transaction)
            return len(self.chain)

        else: #normal transaction from 1 wallet to another
            signature_verification = self.verify_transaction_signature(sender_public_key, signature, transaction)  # verify the signature

            if signature_verification:
                self.transactions.append(transaction)
                return len(self.chain) + 1

            else:
                return False








blockchain = Blockchain() #create an instance

#instantiate the node with flask
app = Flask(__name__)
CORS(app)

@app.route('/') #same idea as a route in ASP.NET
def index():
    return render_template('./index.html') #to translate to ASP.NET, this is a controller that renders a view called index.html


@app.route('/transactions/get')
def get_transactions():
    transactions = blockchain.transactions
    response = {'transactions': transactions}
    return jsonify(response), 200 #response needs to be rendered in JSON because we are using java script for the front end


@app.route('/chain')
def get_chain():
    response = {
        'chain': blockchain.chain,
        'length':len(blockchain.chain)
    }

    return response, 200





@app.route('/mine')
def mine():
    nonce = blockchain.proof_of_word()

    blockchain.submit_transaction(sender_public_key = MINING_SENDER, recipient_public_key=blockchain.node_id, signature='', amount= MINING_REWARD)

    last_block = blockchain.chain[-1] #access last (most recent) block
    previous_hash = blockchain.hash(last_block)

    block = blockchain.create_block(nonce, previous_hash)

    response = {
        'message': 'New block created',
        'block_number': block['block_number'],
        'transactions': block['transactions'],
        'nonce': block['nonce'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 200





@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form
    required = ['confirmation_sender_public_key', 'confirmation_recipient_public_key', 'confirmation_amount' ]

    if not all(k in values for k in required): #all iterates through all items in a collection, makes sure all values in values correspond to the fields in the required list
        return 'Missing Values', 400




    transaction_results = blockchain.submit_transaction(values['confirmation_sender_public_key'], values['confirmation_recipient_public_key'], values['transaction_signature'], values['confirmation_amount'])

    if transaction_results == False:
        response = {'message': 'Invalid transaction/signature'}
        return jsonify(response), 406

    else:
        response = {'message': 'Transaction will be added to the end of Block '+ str(transaction_results)}
        return jsonify(response), 201








if __name__ == '__main__': # check if file was ran as a script or imported as a moduel
    from argparse import ArgumentParser #check arguments from command line

    parser = ArgumentParser() # create instance
    parser.add_argument('-p', '--port', default=5001, type = int, help = 'port to listen to') # add the argument to parser, specify port to listen to
    args = parser.parse_args() # get list of arguments
    port = args.port # get port of arguments

                 #specify server, port from argument, debug=true avoids restarting web server any time there is a change
    app.run(host='127.0.0.1', port=port, debug=True )