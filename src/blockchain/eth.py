from web3 import Web3

class Ethereum:
    def __init__(self, infura_url, private_key):
        self.web3 = Web3(Web3.HTTPProvider(infura_url))
        self.private_key = private_key
        self.account = self.web3.eth.account.from_key(private_key)

    def get_balance(self):
        return self.web3.eth.get_balance(self.account.address)

    def send_transaction(self, to_address, amount):
        nonce = self.web3.eth.getTransactionCount(self.account.address)
        tx = {
            'nonce': nonce,
            'to': to_address,
            'value': self.web3.toWei(amount, 'ether'),
            'gas': 2000000,
            'gasPrice': self.web3.toWei('50', 'gwei'),
        }
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return tx_hash.hex()

    def get_latest_block(self):
        return self.web3.eth.get_block('latest')