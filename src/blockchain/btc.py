class Bitcoin:
    def __init__(self, api_client):
        self.api_client = api_client

    def get_price(self):
        # Implement logic to fetch the current Bitcoin price
        pass

    def get_transaction_info(self, transaction_id):
        # Implement logic to fetch transaction details by transaction ID
        pass

    def create_transaction(self, to_address, amount):
        # Implement logic to create a new Bitcoin transaction
        pass

    def get_balance(self, address):
        # Implement logic to fetch the balance of a Bitcoin address
        pass