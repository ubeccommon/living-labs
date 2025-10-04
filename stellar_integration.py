#!/usr/bin/env python3
"""
Stellar Integration Module - Fixed for current stellar-sdk version
Handles UBECrc token distribution on Stellar network

Design Principles Applied:
- Principle #5: Strict async operations
- Principle #9: Integrated rate limiting
- Principle #10: Clear separation of concerns

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from decimal import Decimal
import aiohttp
from stellar_sdk import Server, Asset, TransactionBuilder, Network, Account, Keypair
from stellar_sdk.exceptions import NotFoundError, BadRequestError

logger = logging.getLogger(__name__)


class StellarReciprocalNetwork:
    """
    Stellar network integration for reciprocal economy
    Manages UBECrc token distribution for environmental observations
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Stellar network connection
        
        Args:
            config: Dictionary with Stellar configuration
                - stellar_horizon_url: Horizon server URL
                - stellar_network: 'public' or 'testnet'
                - ubecrc_asset_code: Token code (UBECrc)
                - ubecrc_issuer: Token issuer public key
                - ubecrc_distributor: Distributor public key
                - ubecrc_distributor_secret: Distributor secret key
        """
        self.horizon_url = config.get('stellar_horizon_url', 'https://horizon.stellar.org')
        self.network = config.get('stellar_network', 'public')
        
        # UBECrc token configuration
        self.asset_code = config.get('ubecrc_asset_code', 'UBECrc')
        self.issuer_public = config.get('ubecrc_issuer')
        self.distributor_public = config.get('ubecrc_distributor')
        self.distributor_secret = config.get('ubecrc_distributor_secret')
        
        # Create Asset object
        if self.issuer_public:
            self.ubecrc_asset = Asset(self.asset_code, self.issuer_public)
        else:
            self.ubecrc_asset = None
            logger.warning("UBECrc issuer not configured")
        
        # Server connection
        self.server = Server(horizon_url=self.horizon_url)
        
        # Network passphrase
        if self.network == 'testnet':
            self.network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE
        else:
            self.network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE
        
        # Check if we can send payments
        self.can_send_payments = bool(
            self.distributor_public and 
            self.distributor_secret and 
            self.ubecrc_asset
        )
        
        # Rate limiting
        self._rate_limit_semaphore = asyncio.Semaphore(5)
        
        logger.info(f"Stellar network initialized ({self.network})")
        logger.info(f"  Can send payments: {self.can_send_payments}")
        if self.distributor_public:
            logger.info(f"  Distributor: {self.distributor_public[:8]}...{self.distributor_public[-8:]}")
    
    async def connect(self) -> None:
        """Initialize connection and check account status"""
        if not self.can_send_payments:
            logger.warning("Stellar payment capability disabled (missing credentials)")
            return
        
        try:
            # Check distributor account
            account_info = await self.get_account_info(self.distributor_public)
            if account_info:
                # Check UBECrc balance
                balance = await self.get_ubecrc_balance(self.distributor_public)
                logger.info(f"Distributor UBECrc balance: {balance}")
            else:
                logger.error("Distributor account not found on network")
                self.can_send_payments = False
        except Exception as e:
            logger.error(f"Failed to connect to Stellar network: {e}")
            self.can_send_payments = False
    
    async def get_account_info(self, account_id: str) -> Optional[Dict]:
        """
        Get account information from Stellar network
        
        Args:
            account_id: Stellar public key
            
        Returns:
            Account information dictionary
        """
        try:
            async with self._rate_limit_semaphore:
                # Use aiohttp for async request
                url = f"{self.horizon_url}/accounts/{account_id}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            return await response.json()
                        elif response.status == 404:
                            logger.debug(f"Account not found: {account_id}")
                            return None
                        else:
                            logger.error(f"Failed to get account info: {response.status}")
                            return None
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    async def get_ubecrc_balance(self, account_id: str) -> Decimal:
        """
        Get UBECrc token balance for an account
        
        Args:
            account_id: Stellar public key
            
        Returns:
            UBECrc balance as Decimal
        """
        account_info = await self.get_account_info(account_id)
        if not account_info:
            return Decimal("0")
        
        # Look for UBECrc balance
        for balance in account_info.get('balances', []):
            if (balance.get('asset_code') == self.asset_code and
                balance.get('asset_issuer') == self.issuer_public):
                return Decimal(balance.get('balance', "0"))
        
        return Decimal("0")
    
    async def send_ubecrc_payment(
        self,
        destination: str,
        amount: str,
        memo: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Send UBECrc tokens to a destination account
        
        Args:
            destination: Recipient's Stellar public key
            amount: Amount of UBECrc to send
            memo: Optional transaction memo
            
        Returns:
            Transaction result dictionary or None if failed
        """
        if not self.can_send_payments:
            logger.error("Cannot send payments - distributor not configured")
            return None
        
        try:
            async with self._rate_limit_semaphore:
                # Get distributor account for sequence number
                source_keypair = Keypair.from_secret(self.distributor_secret)
                
                # Get account info for sequence
                url = f"{self.horizon_url}/accounts/{self.distributor_public}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            logger.error("Failed to get source account")
                            return None
                        account_data = await response.json()
                
                # FIXED: Account constructor now takes just two positional arguments
                # The first is the account ID, the second is the sequence number
                source_account = Account(
                    self.distributor_public,  # account ID (positional)
                    int(account_data['sequence'])  # sequence (positional)
                )
                
                # Build transaction
                transaction = (
                    TransactionBuilder(
                        source_account=source_account,
                        network_passphrase=self.network_passphrase,
                        base_fee=100
                    )
                    .append_payment_op(
                        destination=destination,
                        asset=self.ubecrc_asset,
                        amount=str(amount)
                    )
                    .set_timeout(30)
                )
                
                # Add memo if provided
                if memo:
                    transaction.add_text_memo(memo[:28])  # Stellar memo limit
                
                # Build and sign
                transaction = transaction.build()
                transaction.sign(source_keypair)
                
                # Submit transaction
                submit_url = f"{self.horizon_url}/transactions"
                tx_xdr = transaction.to_xdr()
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        submit_url,
                        data={'tx': tx_xdr},
                        headers={'Content-Type': 'application/x-www-form-urlencoded'}
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            tx_hash = result.get('hash')
                            logger.info(f"Payment sent: {amount} UBECrc to {destination[:8]}... (tx: {tx_hash[:8]}...)")
                            return {
                                "success": True,
                                "transaction_hash": tx_hash,
                                "amount": amount,
                                "destination": destination,
                                "ledger": result.get('ledger')
                            }
                        else:
                            error_data = await response.json()
                            logger.error(f"Transaction failed: {error_data}")
                            return {
                                "success": False,
                                "error": error_data.get('extras', {}).get('result_codes', 'Unknown error')
                            }
                            
        except Exception as e:
            logger.error(f"Failed to send payment: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_trustline(self, account_secret: str) -> bool:
        """
        Create a trustline for UBECrc token
        
        Args:
            account_secret: Secret key of account to add trustline
            
        Returns:
            True if successful
        """
        try:
            keypair = Keypair.from_secret(account_secret)
            account_id = keypair.public_key
            
            # Get account info
            account_info = await self.get_account_info(account_id)
            if not account_info:
                logger.error("Account not found")
                return False
            
            # Check if trustline already exists
            for balance in account_info.get('balances', []):
                if (balance.get('asset_code') == self.asset_code and
                    balance.get('asset_issuer') == self.issuer_public):
                    logger.info("Trustline already exists")
                    return True
            
            # FIXED: Account constructor with positional arguments
            source_account = Account(
                account_id,  # account ID (positional)
                int(account_info['sequence'])  # sequence (positional)
            )
            
            transaction = (
                TransactionBuilder(
                    source_account=source_account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100
                )
                .append_change_trust_op(
                    asset=self.ubecrc_asset
                )
                .set_timeout(30)
                .build()
            )
            
            transaction.sign(keypair)
            
            # Submit transaction
            submit_url = f"{self.horizon_url}/transactions"
            tx_xdr = transaction.to_xdr()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    submit_url,
                    data={'tx': tx_xdr},
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                ) as response:
                    if response.status == 200:
                        logger.info(f"Trustline created for {account_id[:8]}...")
                        return True
                    else:
                        error = await response.json()
                        logger.error(f"Failed to create trustline: {error}")
                        return False
                        
        except Exception as e:
            logger.error(f"Error creating trustline: {e}")
            return False
    
    async def get_transaction(self, tx_hash: str) -> Optional[Dict]:
        """
        Get transaction details by hash
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction details
        """
        try:
            url = f"{self.horizon_url}/transactions/{tx_hash}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            logger.error(f"Error getting transaction: {e}")
            return None
    
    async def health_check(self) -> Dict:
        """Check Stellar service health"""
        try:
            # Check horizon server
            url = f"{self.horizon_url}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    horizon_healthy = response.status == 200
            
            # Check distributor balance if configured
            distributor_balance = "0"
            if self.can_send_payments:
                distributor_balance = await self.get_ubecrc_balance(self.distributor_public)
            
            return {
                "status": "healthy" if horizon_healthy else "unhealthy",
                "service": "stellar",
                "network": self.network,
                "horizon_available": horizon_healthy,
                "can_send_payments": self.can_send_payments,
                "distributor_ubecrc_balance": str(distributor_balance),
                "asset_code": self.asset_code
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "stellar",
                "error": str(e),
                "can_send_payments": False
            }
    
    async def close(self) -> None:
        """Close connections (compatibility method)"""
        logger.info("Stellar service closing")


"""
Attribution: This project uses the services of Claude and Anthropic PBC
to inform our decisions and recommendations.
"""
