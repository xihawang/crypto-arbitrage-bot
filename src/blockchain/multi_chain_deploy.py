"""
多链部署工具 - 支持以太坊、Polygon、Arbitrum、Optimism 等
"""

from typing import Dict, List, Optional
from datetime import datetime
from web3 import Web3
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class Chain:
    """区块链配置"""
    
    def __init__(self, name: str, rpc_url: str, chain_id: int, 
                 explorer_url: str, native_token: str = "ETH"):
        """初始化链配置
        
        Args:
            name: 链名称
            rpc_url: RPC 端点
            chain_id: 链 ID
            explorer_url: 区块浏览器 URL
            native_token: 原生代币符号
        """
        self.name = name
        self.rpc_url = rpc_url
        self.chain_id = chain_id
        self.explorer_url = explorer_url
        self.native_token = native_token
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
    
    @property
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self.web3.is_connected()
    
    @property
    def latest_block(self) -> int:
        """获取最新区块号"""
        return self.web3.eth.block_number
    
    @property
    def gas_price(self) -> int:
        """获取当前 Gas 价格"""
        return self.web3.eth.gas_price


class MultiChainDeployer:
    """多链部署器"""
    
    # 支持的链
    CHAINS = {
        "ethereum": Chain(
            name="Ethereum",
            rpc_url="https://eth.llamarpc.com",
            chain_id=1,
            explorer_url="https://etherscan.io",
            native_token="ETH"
        ),
        "polygon": Chain(
            name="Polygon",
            rpc_url="https://polygon-rpc.com",
            chain_id=137,
            explorer_url="https://polygonscan.com",
            native_token="MATIC"
        ),
        "arbitrum": Chain(
            name="Arbitrum One",
            rpc_url="https://arb1.arbitrum.io/rpc",
            chain_id=42161,
            explorer_url="https://arbiscan.io",
            native_token="ETH"
        ),
        "optimism": Chain(
            name="Optimism",
            rpc_url="https://mainnet.optimism.io",
            chain_id=10,
            explorer_url="https://optimistic.etherscan.io",
            native_token="ETH"
        ),
        "base": Chain(
            name="Base",
            rpc_url="https://mainnet.base.org",
            chain_id=8453,
            explorer_url="https://basescan.org",
            native_token="ETH"
        ),
    }
    
    def __init__(self, private_key: str = ""):
        """初始化部署器
        
        Args:
            private_key: 部署者私钥
        """
        self.private_key = private_key
        self.deployments = {}  # {chain_name: deployment_info}
    
    def get_chain(self, chain_name: str) -> Optional[Chain]:
        """获取链对象
        
        Args:
            chain_name: 链名称
            
        Returns:
            Chain 对象
        """
        return self.CHAINS.get(chain_name.lower())
    
    def check_network_status(self, chain_name: str) -> Dict:
        """检查网络状态
        
        Args:
            chain_name: 链名称
            
        Returns:
            网络状态信息
        """
        chain = self.get_chain(chain_name)
        if not chain:
            return {"status": "error", "message": f"未知的链: {chain_name}"}
        
        try:
            is_connected = chain.is_connected
            latest_block = chain.latest_block if is_connected else None
            gas_price = chain.gas_price if is_connected else None
            
            return {
                "chain": chain.name,
                "chain_id": chain.chain_id,
                "connected": is_connected,
                "latest_block": latest_block,
                "gas_price": gas_price,
                "gas_price_gwei": Web3.from_wei(gas_price, "gwei") if gas_price else None,
                "explorer": chain.explorer_url,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ 检查网络状态失败: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def deploy_contract(self, chain_name: str, contract_abi: Dict, 
                       contract_bytecode: str, constructor_args: List = None) -> Optional[Dict]:
        """部署智能合约
        
        Args:
            chain_name: 链名称
            contract_abi: 合约 ABI
            contract_bytecode: 合约字节码
            constructor_args: 构造函数参数
            
        Returns:
            部署信息
        """
        if not self.private_key:
            logger.error("❌ 未配置私钥，无法部署合约")
            return None
        
        chain = self.get_chain(chain_name)
        if not chain:
            logger.error(f"❌ 未知的链: {chain_name}")
            return None
        
        try:
            logger.info(f"🚀 在 {chain.name} 部署合约...")
            
            # 获取账户
            account = chain.web3.eth.account.from_key(self.private_key)
            
            # 创建合约工厂
            Contract = chain.web3.eth.contract(
                abi=contract_abi,
                bytecode=contract_bytecode
            )
            
            # 构建交易
            constructor_args = constructor_args or []
            tx = Contract.constructor(*constructor_args).build_transaction({
                "from": account.address,
                "nonce": chain.web3.eth.get_transaction_count(account.address),
                "gasPrice": chain.web3.eth.gas_price,
                "gas": 3000000,
                "chainId": chain.chain_id
            })
            
            # 签署交易
            signed_tx = chain.web3.eth.account.sign_transaction(tx, self.private_key)
            
            # 发送交易
            tx_hash = chain.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            logger.info(f"✅ 合约部署交易已提交")
            logger.info(f"   Tx Hash: {tx_hash.hex()}")
            logger.info(f"   区块浏览器: {chain.explorer_url}/tx/{tx_hash.hex()}")
            
            # 等待确认
            tx_receipt = chain.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            
            deployment_info = {
                "chain": chain.name,
                "chain_id": chain.chain_id,
                "contract_address": tx_receipt.contractAddress,
                "transaction_hash": tx_hash.hex(),
                "block_number": tx_receipt.blockNumber,
                "gas_used": tx_receipt.gasUsed,
                "deployer": account.address,
                "deployed_at": datetime.now().isoformat(),
                "explorer_url": f"{chain.explorer_url}/address/{tx_receipt.contractAddress}"
            }
            
            # 保存部署信息
            self.deployments[chain_name] = deployment_info
            
            logger.info(f"✅ 合约部署成功!")
            logger.info(f"   合约地址: {tx_receipt.contractAddress}")
            
            return deployment_info
        
        except Exception as e:
            logger.error(f"❌ 部署失败: {str(e)}")
            return None
    
    def verify_deployment(self, chain_name: str, contract_address: str) -> bool:
        """验证合约部署
        
        Args:
            chain_name: 链名称
            contract_address: 合约地址
            
        Returns:
            是否验证成功
        """
        chain = self.get_chain(chain_name)
        if not chain:
            return False
        
        try:
            code = chain.web3.eth.get_code(contract_address)
            
            if code == b"":
                logger.warning(f"⚠️  {chain_name} 上地址无合约代码")
                return False
            
            logger.info(f"✅ {chain_name} 上的合约已验证")
            logger.info(f"   合约大小: {len(code)} 字节")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ 验证失败: {str(e)}")
            return False
    
    def get_all_networks_status(self) -> List[Dict]:
        """获取所有网络状态"""
        logger.info("🔍 检查所有网络状态...\n")
        
        statuses = []
        for chain_name in self.CHAINS.keys():
            status = self.check_network_status(chain_name)
            statuses.append(status)
            
            if status.get("connected"):
                logger.info(f"✅ {status['chain']}: 已连接 (Block #{status['latest_block']})")
            else:
                logger.warning(f"❌ {status['chain']}: 连接失败")
        
        return statuses
    
    def display_deployment_summary(self) -> None:
        """显示部署总结"""
        if not self.deployments:
            logger.info("📋 暂无部署信息")
            return
        
        print(f"\n{'='*80}")
        print(f"📊 多链部署总结")
        print(f"{'='*80}\n")
        
        print(f"{'链':<15} {'合约地址':<42} {'部署区块':<12} {'状态':<8}")
        print("-" * 80)
        
        for chain_name, info in self.deployments.items():
            contract_addr = info.get("contract_address", "N/A")[:40]
            block_num = info.get("block_number", "N/A")
            print(f"{info['chain']:<15} {contract_addr:<42} {str(block_num):<12} {'✅':<8}")
    
    def list_supported_chains(self) -> None:
        """列出支持的链"""
        print(f"\n{'='*60}")
        print(f"🌐 支持的区块链")
        print(f"{'='*60}\n")
        
        for chain_name, chain in self.CHAINS.items():
            print(f"  • {chain.name} (ID: {chain.chain_id})")
            print(f"    RPC: {chain.rpc_url}")
            print(f"    浏览器: {chain.explorer_url}\n")


# 全局部署器实例
multi_chain_deployer = MultiChainDeployer()
