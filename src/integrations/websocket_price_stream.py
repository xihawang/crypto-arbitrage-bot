"""
WebSocket 实时价格流
使用 WebSocket 连接获取实时价格数据，比 REST API 更快
支持: Binance, Coinbase 等
"""

import asyncio
import json
import logging
from typing import Dict, Callable, Optional, List
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class BinanceWebSocket:
    """币安 WebSocket 连接"""
    
    def __init__(self, symbols: List[str] = None):
        """初始化币安 WebSocket
        
        Args:
            symbols: 交易对列表，如 ["btcusdt", "ethusdt"]
        """
        self.symbols = symbols or ["btcusdt", "ethusdt", "solusdt"]
        self.ws_url = "wss://stream.binance.com:9443/ws"
        self.session = None
        self.is_connected = False
        self.price_callbacks = []
    
    def add_price_callback(self, callback: Callable):
        """添加价格更新回调
        
        Args:
            callback: 异步回调函数，接收 (symbol, price, timestamp)
        """
        self.price_callbacks.append(callback)
    
    async def connect(self):
        """连接到 WebSocket"""
        import websockets
        
        try:
            # 构建 stream 名称
            streams = [f"{symbol}@ticker" for symbol in self.symbols]
            stream_url = f"{self.ws_url}/{'/'.join(streams)}"
            
            logger.info(f"🔗 连接币安 WebSocket: {len(self.symbols)} 个交易对")
            
            self.session = await websockets.connect(stream_url)
            self.is_connected = True
            
            logger.info("✅ 币安 WebSocket 连接成功")
            
            # 接收数据
            await self._receive_messages()
            
        except Exception as e:
            logger.error(f"❌ WebSocket 连接失败: {str(e)}")
            self.is_connected = False
    
    async def _receive_messages(self):
        """接收 WebSocket 消息"""
        try:
            async for message in self.session:
                data = json.loads(message)
                
                # 处理 ticker 数据
                if "s" in data:  # symbol
                    symbol = data["s"].lower()
                    price = float(data["c"])  # close price
                    timestamp = datetime.fromtimestamp(data["E"] / 1000)
                    
                    # 调用所有回调
                    for callback in self.price_callbacks:
                        try:
                            await callback(symbol, price, timestamp)
                        except Exception as e:
                            logger.error(f"❌ 回调执行失败: {str(e)}")
        
        except asyncio.CancelledError:
            logger.info("⏹️  WebSocket 接收已停止")
        except Exception as e:
            logger.error(f"❌ 接收消息错误: {str(e)}")
    
    async def disconnect(self):
        """断开连接"""
        if self.session:
            await self.session.close()
            self.is_connected = False
            logger.info("👋 币安 WebSocket 已断开")


class CoinbaseWebSocket:
    """Coinbase WebSocket 连接"""
    
    def __init__(self, product_ids: List[str] = None):
        """初始化 Coinbase WebSocket
        
        Args:
            product_ids: 产品 ID 列表，如 ["BTC-USD", "ETH-USD"]
        """
        self.product_ids = product_ids or ["BTC-USD", "ETH-USD", "SOL-USD"]
        self.ws_url = "wss://ws-feed.exchange.coinbase.com"
        self.session = None
        self.is_connected = False
        self.price_callbacks = []
    
    def add_price_callback(self, callback: Callable):
        """添加价格更新回调"""
        self.price_callbacks.append(callback)
    
    async def connect(self):
        """连接到 WebSocket"""
        import websockets
        
        try:
            logger.info(f"🔗 连接 Coinbase WebSocket: {len(self.product_ids)} 个产品")
            
            self.session = await websockets.connect(self.ws_url)
            
            # 订阅消息
            subscribe_msg = {
                "type": "subscribe",
                "product_ids": self.product_ids,
                "channels": ["ticker"]
            }
            
            await self.session.send(json.dumps(subscribe_msg))
            self.is_connected = True
            
            logger.info("✅ Coinbase WebSocket 连接成功")
            
            # 接收数据
            await self._receive_messages()
            
        except Exception as e:
            logger.error(f"❌ WebSocket 连接失败: {str(e)}")
            self.is_connected = False
    
    async def _receive_messages(self):
        """接收 WebSocket 消息"""
        try:
            async for message in self.session:
                data = json.loads(message)
                
                # 处理 ticker 消息
                if data.get("type") == "ticker" and "price" in data:
                    product_id = data["product_id"]
                    price = float(data["price"])
                    timestamp = datetime.fromisoformat(data["time"].replace("Z", "+00:00"))
                    
                    # 调用所有回调
                    for callback in self.price_callbacks:
                        try:
                            await callback(product_id, price, timestamp)
                        except Exception as e:
                            logger.error(f"❌ 回调执行失败: {str(e)}")
        
        except asyncio.CancelledError:
            logger.info("⏹️  WebSocket 接收已停止")
        except Exception as e:
            logger.error(f"❌ 接收消息错误: {str(e)}")
    
    async def disconnect(self):
        """断开连接"""
        if self.session:
            await self.session.close()
            self.is_connected = False
            logger.info("👋 Coinbase WebSocket 已断开")


class PriceStreamManager:
    """价格流管理器 - 统一管理多个 WebSocket 连接"""
    
    def __init__(self):
        self.binance_ws = None
        self.coinbase_ws = None
        self.latest_prices: Dict[str, Dict] = {}
        self.tasks = []
    
    def add_price_callback(self, callback: Callable):
        """为所有连接添加价格回调"""
        if self.binance_ws:
            self.binance_ws.add_price_callback(callback)
        if self.coinbase_ws:
            self.coinbase_ws.add_price_callback(callback)
    
    async def default_price_callback(self, symbol: str, price: float, timestamp):
        """默认价格回调 - 保存最新价格"""
        self.latest_prices[symbol] = {
            "price": price,
            "timestamp": timestamp,
            "updated_at": datetime.now()
        }
        logger.debug(f"📊 {symbol.upper()}: ${price:,.2f}")
    
    async def start_binance_stream(self, symbols: List[str] = None):
        """启动币安价格流"""
        try:
            self.binance_ws = BinanceWebSocket(symbols)
            self.binance_ws.add_price_callback(self.default_price_callback)
            
            task = asyncio.create_task(self.binance_ws.connect())
            self.tasks.append(task)
            
            return task
        except Exception as e:
            logger.error(f"❌ 启动币安流失败: {str(e)}")
    
    async def start_coinbase_stream(self, product_ids: List[str] = None):
        """启动 Coinbase 价格流"""
        try:
            self.coinbase_ws = CoinbaseWebSocket(product_ids)
            self.coinbase_ws.add_price_callback(self.default_price_callback)
            
            task = asyncio.create_task(self.coinbase_ws.connect())
            self.tasks.append(task)
            
            return task
        except Exception as e:
            logger.error(f"❌ 启动 Coinbase 流失败: {str(e)}")
    
    async def start_all_streams(self):
        """启动所有价格流"""
        logger.info("\n🚀 启动实时价格流")
        logger.info("="*60)
        
        await self.start_binance_stream()
        await self.start_coinbase_stream()
        
        try:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        except KeyboardInterrupt:
            logger.info("\n🛑 正在停止价格流...")
            await self.stop_all_streams()
    
    async def stop_all_streams(self):
        """停止所有价格流"""
        logger.info("👋 停止所有价格流")
        
        if self.binance_ws:
            await self.binance_ws.disconnect()
        if self.coinbase_ws:
            await self.coinbase_ws.disconnect()
        
        # 取消所有任务
        for task in self.tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """获取最新价格"""
        data = self.latest_prices.get(symbol.lower())
        return data["price"] if data else None
    
    def get_all_latest_prices(self) -> Dict[str, float]:
        """获取所有最新价格"""
        return {symbol: data["price"] for symbol, data in self.latest_prices.items()}


# 全局实例
price_stream_manager = PriceStreamManager()
