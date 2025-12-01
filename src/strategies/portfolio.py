class Portfolio:
    def __init__(self):
        self.assets = {}
    
    def add_asset(self, symbol, amount, price):
        if symbol in self.assets:
            self.assets[symbol]['amount'] += amount
            self.assets[symbol]['total_investment'] += amount * price
        else:
            self.assets[symbol] = {
                'amount': amount,
                'total_investment': amount * price
            }
    
    def remove_asset(self, symbol, amount, price):
        if symbol in self.assets and self.assets[symbol]['amount'] >= amount:
            self.assets[symbol]['amount'] -= amount
            self.assets[symbol]['total_investment'] -= amount * price
            
            if self.assets[symbol]['amount'] == 0:
                del self.assets[symbol]
        else:
            raise ValueError("Insufficient asset amount to remove.")
    
    def calculate_total_value(self, current_prices):
        total_value = 0
        for symbol, data in self.assets.items():
            total_value += data['amount'] * current_prices.get(symbol, 0)
        return total_value
    
    def calculate_roi(self):
        total_investment = sum(data['total_investment'] for data in self.assets.values())
        current_value = self.calculate_total_value({symbol: data['amount'] for symbol, data in self.assets.items()})
        if total_investment == 0:
            return 0
        return (current_value - total_investment) / total_investment * 100