from flask import Flask, render_template, jsonify
from time import time
from flask_cors import CORS

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





blockchain = Blockchain() #create an instance

#instantiate the node with flask
app = Flask(__name__)
CORS(app)

@app.route('/') #same idea as a route in ASP.NET
def index():
    return render_template('./index.html') #to translate to ASP.NET, this is a controller that renders a view called index.html


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    response = {'message':'Ok'}
    return jsonify(response), 201 #201 http code for adding new resource






if __name__ == '__main__': # check if file was ran as a script or imported as a moduel
    from argparse import ArgumentParser #check arguments from command line

    parser = ArgumentParser() # create instance
    parser.add_argument('-p', '--port', default=5001, type = int, help = 'port to listen to') # add the argument to parser, specify port to listen to
    args = parser.parse_args() # get list of arguments
    port = args.port # get port of arguments

                 #specify server, port from argument, debug=true avoids restarting web server any time there is a change
    app.run(host='127.0.0.1', port=port, debug=True )