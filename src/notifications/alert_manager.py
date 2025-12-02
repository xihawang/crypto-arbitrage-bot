"""
告警管理器 - 多渠道告警系统
支持: Telegram、邮件、Webhook
"""

import asyncio
import aiohttp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional
from src.utils.logger import logger
from src.config import (
    ALERT_ENABLED, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    EMAIL_ENABLED, SMTP_SERVER, SMTP_PORT, EMAIL_USER, EMAIL_PASSWORD,
    ALERT_WEBHOOK_URL
)


class AlertManager:
    """告警管理器"""

    def __init__(self):
        self.session = None
        self.last_alerts = {}  # 防止重复告警
        self.alert_cooldown = 300  # 5分钟冷却期

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _should_send_alert(self, alert_key: str) -> bool:
        """检查是否应该发送告警（避免重复）"""
        now = datetime.now().timestamp()
        if alert_key in self.last_alerts:
            if now - self.last_alerts[alert_key] < self.alert_cooldown:
                return False
        self.last_alerts[alert_key] = now
        return True

    async def send_telegram_alert(self, message: str) -> bool:
        """发送Telegram告警"""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            logger.debug("Telegram配置不完整，跳过发送")
            return False

        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            }

            async with self.session.post(url, json=data, timeout=10) as response:
                if response.status == 200:
                    logger.info("✅ Telegram告警发送成功")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Telegram告警发送失败: {error_text}")
                    return False

        except Exception as e:
            logger.error(f"❌ Telegram告警发送错误: {e}")
            return False

    async def send_email_alert(self, subject: str, message: str) -> bool:
        """发送邮件告警"""
        if not EMAIL_ENABLED or not EMAIL_USER or not EMAIL_PASSWORD:
            logger.debug("邮件配置不完整，跳过发送")
            return False

        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = EMAIL_USER
            msg['Subject'] = f"[套利机器人] {subject}"

            # 邮件内容
            body = f"""
            <html>
            <body>
                <h2 style="color: #e74c3c;">🚨 套利机会告警</h2>
                <div style="font-family: Arial, sans-serif; line-height: 1.6;">
                    {message}
                </div>
                <hr>
                <p style="color: #7f8c8d; font-size: 12px;">
                    发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                    此邮件由加密货币套利机器人自动发送
                </p>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))

            # 发送邮件
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()

            logger.info("✅ 邮件告警发送成功")
            return True

        except Exception as e:
            logger.error(f"❌ 邮件告警发送错误: {e}")
            return False

    async def send_webhook_alert(self, data: Dict) -> bool:
        """发送Webhook告警"""
        if not ALERT_WEBHOOK_URL:
            logger.debug("Webhook URL未配置，跳过发送")
            return False

        try:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "source": "crypto-arbitrage-bot",
                "type": "arbitrage_opportunity",
                "data": data
            }

            async with self.session.post(
                ALERT_WEBHOOK_URL,
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status in [200, 201, 204]:
                    logger.info("✅ Webhook告警发送成功")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Webhook告警发送失败: {error_text}")
                    return False

        except Exception as e:
            logger.error(f"❌ Webhook告警发送错误: {e}")
            return False

    def format_arbitrage_alert(self, opportunity: Dict) -> str:
        """格式化套利机会告警消息"""
        emoji = "🚀" if opportunity['diff_rate'] >= 5 else "⚡" if opportunity['diff_rate'] >= 3 else "💰"

        message = f"""
{emoji} <b>套利机会发现！</b>

📊 <b>币种:</b> {opportunity['crypto']}
💰 <b>差价率:</b> {opportunity['diff_rate']:.2f}%
📈 <b>买入:</b> {opportunity['buy_exchange']} @ ${opportunity['buy_price']:,.2f}
📉 <b>卖出:</b> {opportunity['sell_exchange']} @ ${opportunity['sell_price']:,.2f}
💵 <b>预期利润:</b> ${opportunity['potential_profit']:.2f}

⏰ <b>时间:</b> {datetime.now().strftime('%H:%M:%S')}
🔗 <b>状态:</b> 立即执行可获利
        """.strip()

        return message

    async def send_arbitrage_alert(self, opportunity: Dict) -> bool:
        """发送套利机会告警"""
        if not ALERT_ENABLED:
            return False

        alert_key = f"{opportunity['crypto']}_{opportunity['buy_exchange']}_{opportunity['sell_exchange']}"
        if not self._should_send_alert(alert_key):
            return False

        message = self.format_arbitrage_alert(opportunity)
        subject = f"套利机会: {opportunity['crypto']} ({opportunity['diff_rate']:.2f}%)"

        # 并发发送所有告警渠道
        tasks = []

        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            tasks.append(self.send_telegram_alert(message))

        if EMAIL_ENABLED:
            tasks.append(self.send_email_alert(subject, message))

        if ALERT_WEBHOOK_URL:
            tasks.append(self.send_webhook_alert(opportunity))

        # 等待所有任务完成
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = sum(1 for r in results if r is True)
            logger.info(f"📊 套利告警发送完成: {success_count}/{len(tasks)} 个渠道成功")

        return True

    async def send_system_alert(self, title: str, message: str, level: str = "info") -> bool:
        """发送系统告警"""
        if not ALERT_ENABLED:
            return False

        alert_key = f"system_{title}_{level}"
        if not self._should_send_alert(alert_key):
            return False

        emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅"
        }.get(level, "ℹ️")

        full_message = f"{emoji} <b>{title}</b>\n\n{message}\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        tasks = []

        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            tasks.append(self.send_telegram_alert(full_message))

        if EMAIL_ENABLED and level in ["error", "warning"]:
            tasks.append(self.send_email_alert(f"[{level.upper()}] {title}", full_message))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        return True

    async def send_daily_summary(self, opportunities: List[Dict], total_profit: float) -> bool:
        """发送每日汇总报告"""
        if not ALERT_ENABLED or not opportunities:
            return False

        emoji = "📊"
        message = f"""
{emoji} <b>每日套利汇总报告</b>

📈 <b>发现机会:</b> {len(opportunities)} 个
💰 <b>预期总利润:</b> ${total_profit:.2f}

<b>今日最佳机会:</b>
        """

        if opportunities:
            best = opportunities[0]
            message += f"""
🥇 {best['crypto']}: {best['diff_rate']:.2f}% (${best['potential_profit']:.2f})
   买入: {best['buy_exchange']} @ ${best['buy_price']:,.2f}
   卖出: {best['sell_exchange']} @ ${best['sell_price']:,.2f}
            """

        message += f"\n\n⏰ 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        tasks = []

        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            tasks.append(self.send_telegram_alert(message))

        if EMAIL_ENABLED:
            tasks.append(self.send_email_alert("每日套利汇总报告", message))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        return True


# 全局实例
alert_manager = AlertManager()


async def send_arbitrage_alert(opportunity: Dict) -> bool:
    """发送套利告警的便捷函数"""
    async with alert_manager as manager:
        return await manager.send_arbitrage_alert(opportunity)


async def send_system_alert(title: str, message: str, level: str = "info") -> bool:
    """发送系统告警的便捷函数"""
    async with alert_manager as manager:
        return await manager.send_system_alert(title, message, level)


if __name__ == "__main__":
    # 测试代码
    async def test_alerts():
        opportunity = {
            "crypto": "BTC",
            "diff_rate": 3.5,
            "buy_exchange": "binance",
            "sell_exchange": "okx",
            "buy_price": 45000,
            "sell_price": 46650,
            "potential_profit": 1650
        }

        async with AlertManager() as manager:
            await manager.send_arbitrage_alert(opportunity)
            await manager.send_system_alert("测试消息", "这是一个测试系统告警", "info")

    asyncio.run(test_alerts())