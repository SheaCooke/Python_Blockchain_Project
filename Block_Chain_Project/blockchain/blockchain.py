from flask import Flask, render_template, jsonify, request
from time import time
from flask_cors import CORS
from collections import OrderedDict

class Blockchain:
    def __init__(self):
        self.transactions = []
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
    def submit_transaction(self, sender_public_key, recipient_public_key, signature, amount):
        # TODO: reward the miner
        # TODO: signature validation

        transaction = OrderedDict({
            'sender_public_key': sender_public_key,
            'recipient_public_key': recipient_public_key,
            'signature': signature,
            'amount':amount
        })
        signature_verification = True #verify the signature

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


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form
    transaction_results = blockchain.submit_transaction(values['confirmation_sender_public_key'], values['confirmation_recipient_public_key'], values['transaction_signature'], values['confirmation_amount'])

    if transaction_results == False:
        response = {'message': 'Invalid transaction/signature'}
        return jsonify(response), 406

    else:
        response = {'message': 'Transaction will be added to the Block '+ str(transaction_results)}
        return jsonify(response), 201








if __name__ == '__main__': # check if file was ran as a script or imported as a moduel
    from argparse import ArgumentParser #check arguments from command line

    parser = ArgumentParser() # create instance
    parser.add_argument('-p', '--port', default=5001, type = int, help = 'port to listen to') # add the argument to parser, specify port to listen to
    args = parser.parse_args() # get list of arguments
    port = args.port # get port of arguments

                 #specify server, port from argument, debug=true avoids restarting web server any time there is a change
    app.run(host='127.0.0.1', port=port, debug=True )