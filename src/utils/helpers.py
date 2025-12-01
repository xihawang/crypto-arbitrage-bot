def calculate_profit(buy_price, sell_price, quantity):
    return (sell_price - buy_price) * quantity

def is_arbitrage_opportunity(buy_price, sell_price, threshold=0):
    return (sell_price - buy_price) > threshold

def format_currency(amount):
    return f"{amount:.2f}"

def validate_price(price):
    if price <= 0:
        raise ValueError("Price must be greater than zero.")
    return price

def get_current_timestamp():
    from datetime import datetime
    return datetime.now().isoformat()