import time
from exchanges.binance import Binance
from exchanges.coinbase import Coinbase
from exchanges.kraken import Kraken
from strategies.arbitrage import Arbitrage
from utils.logger import Logger

def main():
    logger = Logger()
    logger.info("Starting Crypto Arbitrage Bot...")

    # Initialize exchanges
    binance = Binance()
    coinbase = Coinbase()
    kraken = Kraken()

    # Initialize arbitrage strategy
    arbitrage_strategy = Arbitrage([binance, coinbase, kraken])

    try:
        while True:
            logger.info("Checking for arbitrage opportunities...")
            opportunities = arbitrage_strategy.find_opportunities()
            if opportunities:
                for opportunity in opportunities:
                    logger.info(f"Arbitrage opportunity found: {opportunity}")
                    arbitrage_strategy.execute_trade(opportunity)
            else:
                logger.info("No arbitrage opportunities found.")
            time.sleep(10)  # Wait before checking again
    except KeyboardInterrupt:
        logger.info("Arbitrage Bot stopped by user.")

if __name__ == "__main__":
    main()