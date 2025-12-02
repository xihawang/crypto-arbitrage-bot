import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ============ 支持的加密货币 ============
CRYPTOS = ["BTC", "ETH", "SOL", "USDT", "USDC"]

# ============ 交易所配置 ============
EXCHANGES = {
    "binance": {
        "api_key": os.getenv("BINANCE_API_KEY", ""),
        "api_secret": os.getenv("BINANCE_API_SECRET", ""),
        "base_url": "https://api.binance.com",
        "enabled": True
    },
    "coinbase": {
        "api_key": os.getenv("COINBASE_API_KEY", ""),
        "api_secret": os.getenv("COINBASE_API_SECRET", ""),
        "base_url": "https://api.coinbase.com",
        "enabled": True
    },
    "kraken": {
        "api_key": os.getenv("KRAKEN_API_KEY", ""),
        "api_secret": os.getenv("KRAKEN_API_SECRET", ""),
        "base_url": "https://api.kraken.com",
        "enabled": False
    },
    "okx": {
        "api_key": os.getenv("OKX_API_KEY", ""),
        "api_secret": os.getenv("OKX_API_SECRET", ""),
        "passphrase": os.getenv("OKX_PASSPHRASE", ""),
        "base_url": "https://www.okx.com",
        "enabled": True
    },
    "bybit": {
        "api_key": os.getenv("BYBIT_API_KEY", ""),
        "api_secret": os.getenv("BYBIT_API_SECRET", ""),
        "base_url": "https://api.bybit.com",
        "enabled": True
    },
    "bitget": {
        "api_key": os.getenv("BITGET_API_KEY", ""),
        "api_secret": os.getenv("BITGET_API_SECRET", ""),
        "passphrase": os.getenv("BITGET_PASSPHRASE", ""),
        "base_url": "https://api.bitget.com",
        "enabled": True
    }
}

# ============ 套利配置 ============
ARBITRAGE_THRESHOLD = 2.0  # 最小套利差价 2%
SCAN_INTERVAL = 10  # 扫描间隔 10 秒 (优化为高频扫描)

# ============ 数据库配置 ============
DB_URL = os.getenv("DATABASE_URL", "sqlite:///arbitrage.db")

# ============ 日志配置 ============
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============ API 配置 ============
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")
API_PORT = int(os.getenv("API_PORT", 5000))

# ============ WebSocket 配置 ============
WS_ENABLED = os.getenv("WS_ENABLED", "True") == "True"
WS_RECONNECT_INTERVAL = 5  # WebSocket 重连间隔

# ============ 机器学习配置 ============
ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", "models/")
ML_PREDICTION_INTERVAL = 3600  # 预测间隔 1 小时

# ============ 告警配置 ============
ALERT_ENABLED = os.getenv("ALERT_ENABLED", "True") == "True"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "False") == "True"
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
ALERT_WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL", "")

# ============ 自动交易配置 ============
AUTO_TRADE_ENABLED = os.getenv("AUTO_TRADE_ENABLED", "False") == "True"
MIN_PROFIT_THRESHOLD = float(os.getenv("MIN_PROFIT_THRESHOLD", 0.01))  # 最小利润率 1%
MAX_TRADE_SIZE = float(os.getenv("MAX_TRADE_SIZE", 1000))  # 最大交易金额
TRADE_DELAY_SECONDS = int(os.getenv("TRADE_DELAY_SECONDS", 2))  # 交易延迟
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "True") == "True"  # 模拟模式
DRY_RUN = os.getenv("DRY_RUN", "True") == "True"  # 试运行模式

# ============ 风险管理配置 ============
MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", 1000))  # 最大持仓
MAX_DAILY_LOSS = float(os.getenv("MAX_DAILY_LOSS", 500))  # 最大日亏损
STOP_LOSS_PERCENT = float(os.getenv("STOP_LOSS_PERCENT", 2.0))  # 止损百分比

# ============ 旧版兼容 ============
class Config:
    def __init__(self):
        self.API_KEYS = {
            'binance': os.getenv('BINANCE_API_KEY'),
            'coinbase': os.getenv('COINBASE_API_KEY'),
            'kraken': os.getenv('KRAKEN_API_KEY')
        }
        self.EXCHANGE_URLS = {
            'binance': 'https://api.binance.com',
            'coinbase': 'https://api.coinbase.com',
            'kraken': 'https://api.kraken.com'
        }
        self.TRADE_SETTINGS = {
            'slippage': 0.01,
            'min_profit': 0.01
        }
        self.LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')

config = Config()