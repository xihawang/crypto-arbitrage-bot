from solana.rpc.api import Client

class Solana:
    def __init__(self, rpc_url):
        self.client = Client(rpc_url)

    def get_price(self, token_mint_address):
        # This function should implement logic to get the price of a token on Solana
        # For now, it returns a placeholder value
        return 0.0

    def get_balance(self, wallet_address):
        response = self.client.get_balance(wallet_address)
        return response['result']['value'] / 1_000_000_000  # Convert lamports to SOL

    def send_transaction(self, transaction):
        response = self.client.send_transaction(transaction)
        return response

    def get_transaction_history(self, wallet_address):
        response = self.client.get_confirmed_signature_for_address2(wallet_address)
        return response['result']