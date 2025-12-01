from coinbase.wallet.client import Client

class CoinbaseExchange:
    def __init__(self, api_key, api_secret):
        self.client = Client(api_key, api_secret)

    def get_market_data(self, currency_pair):
        try:
            price = self.client.get_spot_price(currency_pair=currency_pair)
            return float(price.amount)
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return None

    def place_order(self, order_type, amount, currency):
        try:
            if order_type == 'buy':
                order = self.client.buy(amount=amount, currency=currency)
            elif order_type == 'sell':
                order = self.client.sell(amount=amount, currency=currency)
            return order
        except Exception as e:
            print(f"Error placing order: {e}")
            return None

    def get_account_balance(self):
        try:
            accounts = self.client.get_accounts()
            return {account['currency']: account['balance']['amount'] for account in accounts['data']}
        except Exception as e:
            print(f"Error fetching account balance: {e}")
            return None