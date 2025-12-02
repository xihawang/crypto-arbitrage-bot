"""
Telegram 机器人集成 - 实时交易和套利机会通知
"""

import requests
from typing import Dict, Optional, List
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TelegramBot:
    """Telegram 机器人"""
    
    def __init__(self, bot_token: str = "", chat_id: str = ""):
        """初始化 Telegram 机器人
        
        Args:
            bot_token: 机器人 Token (从 @BotFather 获取)
            chat_id: 聊天 ID (从 @userinfobot 获取)
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.session = requests.Session()
    
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """发送文本消息
        
        Args:
            text: 消息文本 (支持 HTML 格式)
            parse_mode: 解析模式 (HTML 或 Markdown)
            
        Returns:
            是否发送成功
        """
        if not self.bot_token or not self.chat_id:
            logger.warning("⚠️  未配置 Telegram 凭证，无法发送消息")
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.debug(f"✅ Telegram 消息已发送")
            return True
        
        except Exception as e:
            logger.error(f"❌ 发送 Telegram 消息失败: {str(e)}")
            return False
    
    def send_document(self, document_path: str, caption: str = "") -> bool:
        """发送文件
        
        Args:
            document_path: 文件路径
            caption: 文件说明
            
        Returns:
            是否发送成功
        """
        if not self.bot_token or not self.chat_id:
            logger.warning("⚠️  未配置 Telegram 凭证")
            return False
        
        try:
            url = f"{self.base_url}/sendDocument"
            
            with open(document_path, "rb") as f:
                files = {"document": f}
                data = {
                    "chat_id": self.chat_id,
                    "caption": caption
                }
                
                response = self.session.post(url, files=files, data=data, timeout=30)
                response.raise_for_status()
            
            logger.info(f"✅ 文档已发送: {document_path}")
            return True
        
        except Exception as e:
            logger.error(f"❌ 发送文档失败: {str(e)}")
            return False
    
    def send_arbitrage_alert(self, arbitrage_data: Dict) -> bool:
        """发送套利机会通知
        
        Args:
            arbitrage_data: 套利数据
            
        Returns:
            是否发送成功
        """
        try:
            crypto = arbitrage_data.get("crypto", "N/A")
            diff_rate = arbitrage_data.get("diff_rate", 0)
            buy_exchange = arbitrage_data.get("buy_exchange", "N/A")
            buy_price = arbitrage_data.get("buy_price", 0)
            sell_exchange = arbitrage_data.get("sell_exchange", "N/A")
            sell_price = arbitrage_data.get("sell_price", 0)
            
            message = f"""
🚨 <b>发现套利机会!</b>

<b>币种:</b> {crypto}
<b>差价率:</b> {diff_rate:.4f}%

<b>买入:</b> {buy_exchange}
💰 价格: ${buy_price:,.2f}

<b>卖出:</b> {sell_exchange}
💰 价格: ${sell_price:,.2f}

⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            return self.send_message(message)
        
        except Exception as e:
            logger.error(f"❌ 发送套利通知失败: {str(e)}")
            return False
    
    def send_trade_notification(self, trade_data: Dict) -> bool:
        """发送交易通知
        
        Args:
            trade_data: 交易数据
            
        Returns:
            是否发送成功
        """
        try:
            action = trade_data.get("action", "交易")  # OPEN/CLOSE
            crypto = trade_data.get("crypto", "N/A")
            quantity = trade_data.get("quantity", 0)
            price = trade_data.get("price", 0)
            pnl = trade_data.get("pnl", 0)
            pnl_rate = trade_data.get("pnl_rate", 0)
            
            if action.upper() == "OPEN":
                side = trade_data.get("side", "LONG")
                message = f"""
📊 <b>开仓通知</b>

方向: <b>{side}</b>
币种: <b>{crypto}</b>
数量: {quantity}
价格: ${price:,.2f}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            else:  # CLOSE
                message = f"""
✅ <b>平仓通知</b>

币种: <b>{crypto}</b>
数量: {quantity}
平仓价: ${price:,.2f}
收益: ${pnl:,.2f} ({pnl_rate:.2f}%)

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            return self.send_message(message)
        
        except Exception as e:
            logger.error(f"❌ 发送交易通知失败: {str(e)}")
            return False
    
    def send_error_alert(self, error_msg: str) -> bool:
        """发送错误警告
        
        Args:
            error_msg: 错误消息
            
        Returns:
            是否发送成功
        """
        message = f"""
❌ <b>错误警告</b>

{error_msg}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return self.send_message(message)
    
    def send_daily_report(self, report_data: Dict) -> bool:
        """发送日报
        
        Args:
            report_data: 日报数据
            
        Returns:
            是否发送成功
        """
        try:
            opportunities = report_data.get("opportunities", 0)
            trades = report_data.get("trades", 0)
            total_pnl = report_data.get("total_pnl", 0)
            best_trade = report_data.get("best_trade", "N/A")
            
            message = f"""
📈 <b>每日报告</b>

扫描币种: {report_data.get('cryptos_scanned', 0)} 种
发现机会: {opportunities} 个
执行交易: {trades} 笔

总收益: ${total_pnl:,.2f}
最佳交易: {best_trade}

⏰ {datetime.now().strftime('%Y-%m-%d')}
"""
            
            return self.send_message(message)
        
        except Exception as e:
            logger.error(f"❌ 发送日报失败: {str(e)}")
            return False


class NotificationManager:
    """通知管理器 - 统一管理多个通知渠道"""
    
    def __init__(self, telegram_token: str = "", telegram_chat_id: str = ""):
        """初始化通知管理器"""
        self.telegram = TelegramBot(telegram_token, telegram_chat_id)
    
    def notify_arbitrage_opportunity(self, arbitrage_data: Dict) -> None:
        """通知套利机会"""
        logger.info("📢 发送套利机会通知...")
        self.telegram.send_arbitrage_alert(arbitrage_data)
    
    def notify_trade_opened(self, trade_data: Dict) -> None:
        """通知开仓"""
        logger.info("📢 发送开仓通知...")
        trade_data["action"] = "OPEN"
        self.telegram.send_trade_notification(trade_data)
    
    def notify_trade_closed(self, trade_data: Dict) -> None:
        """通知平仓"""
        logger.info("📢 发送平仓通知...")
        trade_data["action"] = "CLOSE"
        self.telegram.send_trade_notification(trade_data)
    
    def notify_error(self, error_msg: str) -> None:
        """通知错误"""
        logger.error(f"📢 发送错误通知: {error_msg}")
        self.telegram.send_error_alert(error_msg)
    
    def send_daily_report(self, report_data: Dict) -> None:
        """发送日报"""
        logger.info("📢 发送日报...")
        self.telegram.send_daily_report(report_data)


# 全局通知管理器实例
notification_manager = NotificationManager()
