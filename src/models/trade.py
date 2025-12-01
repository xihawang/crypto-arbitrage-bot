class Trade:
    def __init__(self, trade_id, asset, amount, price, trade_type, timestamp):
        self.trade_id = trade_id
        self.asset = asset
        self.amount = amount
        self.price = price
        self.trade_type = trade_type  # 'buy' or 'sell'
        self.timestamp = timestamp

    def get_trade_value(self):
        return self.amount * self.price

    def __repr__(self):
        return f"Trade(trade_id={self.trade_id}, asset={self.asset}, amount={self.amount}, price={self.price}, trade_type={self.trade_type}, timestamp={self.timestamp})"