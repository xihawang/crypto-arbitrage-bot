from krakenex import API

class KrakenExchange:
    def __init__(self, api_key, api_secret):
        self.api = API(api_key=api_key, api_secret=api_secret)

    def get_market_data(self, pair):
        response = self.api.query_public('Ticker', {'pair': pair})
        if response['error']:
            raise Exception(f"Error fetching market data: {response['error']}")
        return response['result']

    def place_order(self, pair, order_type, volume, price=None):
        order_data = {
            'pair': pair,
            'type': order_type,
            'volume': volume,
        }
        if price:
            order_data['price'] = price
        response = self.api.query_private('AddOrder', order_data)
        if response['error']:
            raise Exception(f"Error placing order: {response['error']}")
        return response['result']