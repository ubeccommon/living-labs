#!/usr/bin/env python3
"""
Stellar Onboarding Service
Guides new stewards through Stellar wallet creation, funding, and UBECrc trustline setup

Design Principles Applied:
- Principle #2: Service pattern - no standalone execution
- Principle #4: Single source of truth - database for account records
- Principle #5: Strict async operations
- Principle #9: Integrated rate limiting
- Principle #10: Clear separation of concerns
- Principle #12: Method singularity - unique methods only

Attribution: This project uses the services of Claude and Anthropic PBC to inform our 
decisions and recommendations. This project was made possible with the assistance of 
Claude and Anthropic PBC.
"""

import logging
import asyncio
from typing import Dict, Optional, Tuple
from decimal import Decimal
import aiohttp
from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Account
from stellar_sdk.exceptions import NotFoundError, BadRequestError

logger = logging.getLogger(__name__)


class StellarOnboardingService:
    """
    Handles complete onboarding flow for new Stellar users
    - Generates new wallets
    - Funds accounts with minimum XLM
    - Creates UBECrc trustlines
    - Provides secure credential delivery
    """
    
    # Stellar minimum account balance + buffer
    MIN_ACCOUNT_BALANCE = Decimal("5.0")  # 5 XLM minimum
    TRUSTLINE_RESERVE = Decimal("0.5")    # Additional reserve for trustline
    FUNDING_AMOUNT = MIN_ACCOUNT_BALANCE + TRUSTLINE_RESERVE
    
    def __init__(self, config: Dict):
        """
        Initialize onboarding service
        
        Args:
            config: Configuration dictionary with:
                - stellar_horizon_url: Horizon server URL
                - stellar_network: 'public' or 'testnet'
                - funding_source_public: Funding account public key
                - funding_source_secret: Funding account secret key
                - ubecrc_asset_code: Token code
                - ubecrc_issuer: Token issuer public key
        """
        self.horizon_url = config.get('stellar_horizon_url', 'https://horizon.stellar.org')
        self.network = config.get('stellar_network', 'public')
        
        # Funding account (distributor or dedicated funding account)
        self.funding_public = config.get('funding_source_public')
        self.funding_secret = config.get('funding_source_secret')
        
        # UBECrc token configuration
        self.asset_code = config.get('ubecrc_asset_code', 'UBECrc')
        self.issuer_public = config.get('ubecrc_issuer')
        
        # Server and network
        self.server = Server(horizon_url=self.horizon_url)
        if self.network == 'testnet':
            self.network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE
        else:
            self.network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE
        
        # Rate limiting
        self._rate_limit_semaphore = asyncio.Semaphore(3)
        
        # Validate configuration
        self.is_configured = bool(
            self.funding_public and 
            self.funding_secret and 
            self.issuer_public
        )
        
        if not self.is_configured:
            logger.warning("Stellar onboarding service not fully configured")
        else:
            logger.info(f"Stellar onboarding service initialized ({self.network})")
    
    async def create_and_fund_account(
        self,
        steward_email: str,
        steward_name: str
    ) -> Optional[Dict]:
        """
        Complete onboarding: create wallet, fund it, add trustline
        
        Args:
            steward_email: Steward's email for notification
            steward_name: Steward's name for records
            
        Returns:
            Dictionary with wallet credentials and status, or None if failed
        """
        if not self.is_configured:
            logger.error("Cannot create account - service not configured")
            return None
        
        try:
            # Step 1: Generate new keypair
            new_keypair = Keypair.random()
            public_key = new_keypair.public_key
            secret_key = new_keypair.secret
            
            logger.info(f"Generated new wallet for {steward_name}: {public_key[:8]}...")
            
            # Step 2: Fund the account
            funding_success = await self._fund_new_account(public_key)
            if not funding_success:
                logger.error(f"Failed to fund account {public_key[:8]}...")
                return None
            
            # Step 3: Create UBECrc trustline
            trustline_success = await self._create_trustline(secret_key)
            if not trustline_success:
                logger.warning(f"Account funded but trustline failed for {public_key[:8]}...")
                # Account is still usable, just missing trustline
            
            # Step 4: Verify account status
            account_info = await self._get_account_info(public_key)
            
            return {
                'success': True,
                'public_key': public_key,
                'secret_key': secret_key,  # CRITICAL: Handle securely!
                'funded': True,
                'trustline_created': trustline_success,
                'xlm_balance': self._get_xlm_balance(account_info),
                'steward_email': steward_email,
                'steward_name': steward_name,
                'network': self.network
            }
            
        except Exception as e:
            logger.error(f"Onboarding failed: {e}", exc_info=True)
            return None
    
    async def _fund_new_account(self, destination_public: str) -> bool:
        """
        Fund a new account with minimum XLM
        
        Args:
            destination_public: Public key of account to fund
            
        Returns:
            True if funding successful
        """
        try:
            async with self._rate_limit_semaphore:
                # Get funding account for sequence number
                funding_keypair = Keypair.from_secret(self.funding_secret)
                
                # Get source account info
                url = f"{self.horizon_url}/accounts/{self.funding_public}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            logger.error("Failed to get funding account")
                            return False
                        account_data = await response.json()
                
                # Create source account object
                source_account = Account(
                    self.funding_public,
                    int(account_data['sequence'])
                )
                
                # Build create account transaction
                transaction = (
                    TransactionBuilder(
                        source_account=source_account,
                        network_passphrase=self.network_passphrase,
                        base_fee=100
                    )
                    .append_create_account_op(
                        destination=destination_public,
                        starting_balance=str(self.FUNDING_AMOUNT)
                    )
                    .set_timeout(30)
                    .build()
                )
                
                # Sign transaction
                transaction.sign(funding_keypair)
                
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
                            logger.info(f"Account funded: {destination_public[:8]}... with {self.FUNDING_AMOUNT} XLM")
                            return True
                        else:
                            error = await response.json()
                            logger.error(f"Failed to fund account: {error}")
                            return False
                            
        except Exception as e:
            logger.error(f"Error funding account: {e}", exc_info=True)
            return False
    
    async def _create_trustline(self, account_secret: str) -> bool:
        """
        Create UBECrc trustline for the new account
        
        Args:
            account_secret: Secret key of the new account
            
        Returns:
            True if trustline created successfully
        """
        try:
            async with self._rate_limit_semaphore:
                keypair = Keypair.from_secret(account_secret)
                account_id = keypair.public_key
                
                # Get account info
                account_info = await self._get_account_info(account_id)
                if not account_info:
                    logger.error("Account not found for trustline creation")
                    return False
                
                # Check if trustline already exists
                for balance in account_info.get('balances', []):
                    if (balance.get('asset_code') == self.asset_code and
                        balance.get('asset_issuer') == self.issuer_public):
                        logger.info("Trustline already exists")
                        return True
                
                # Create account object
                source_account = Account(
                    account_id,
                    int(account_info['sequence'])
                )
                
                # Build trustline transaction
                from stellar_sdk import Asset
                ubecrc_asset = Asset(self.asset_code, self.issuer_public)
                
                transaction = (
                    TransactionBuilder(
                        source_account=source_account,
                        network_passphrase=self.network_passphrase,
                        base_fee=100
                    )
                    .append_change_trust_op(
                        asset=ubecrc_asset
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
                            logger.info(f"UBECrc trustline created for {account_id[:8]}...")
                            return True
                        else:
                            error = await response.json()
                            logger.error(f"Failed to create trustline: {error}")
                            return False
                            
        except Exception as e:
            logger.error(f"Error creating trustline: {e}", exc_info=True)
            return False
    
    async def _get_account_info(self, account_id: str) -> Optional[Dict]:
        """
        Get account information from Stellar network
        
        Args:
            account_id: Stellar public key
            
        Returns:
            Account information dictionary
        """
        try:
            url = f"{self.horizon_url}/accounts/{account_id}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.debug(f"Account not found: {account_id}")
                        return None
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def _get_xlm_balance(self, account_info: Optional[Dict]) -> Decimal:
        """
        Extract XLM balance from account info
        
        Args:
            account_info: Account data from Horizon API
            
        Returns:
            XLM balance as Decimal
        """
        if not account_info:
            return Decimal("0")
        
        for balance in account_info.get('balances', []):
            if balance.get('asset_type') == 'native':
                return Decimal(balance.get('balance', "0"))
        
        return Decimal("0")
    
    async def check_funding_account_balance(self) -> Dict:
        """
        Check if funding account has sufficient XLM to create new accounts
        
        Returns:
            Dictionary with balance status and warnings
        """
        if not self.is_configured:
            return {
                'configured': False,
                'error': 'Funding account not configured'
            }
        
        try:
            account_info = await self._get_account_info(self.funding_public)
            xlm_balance = self._get_xlm_balance(account_info)
            
            # Calculate how many accounts can be created
            accounts_possible = int(xlm_balance / self.FUNDING_AMOUNT)
            
            # Warn if running low
            warning = None
            if accounts_possible < 10:
                warning = f"Low funding balance: only {accounts_possible} accounts can be created"
            
            return {
                'configured': True,
                'xlm_balance': float(xlm_balance),
                'funding_amount_per_account': float(self.FUNDING_AMOUNT),
                'accounts_possible': accounts_possible,
                'warning': warning
            }
            
        except Exception as e:
            logger.error(f"Error checking funding account: {e}")
            return {
                'configured': True,
                'error': str(e)
            }
    
    async def has_stellar_account(self, public_key: str) -> bool:
        """
        Check if a Stellar public key corresponds to an existing account
        
        Args:
            public_key: Stellar public key to check
            
        Returns:
            True if account exists on network
        """
        account_info = await self._get_account_info(public_key)
        return account_info is not None
    
    async def add_trustline_to_existing_account(
        self,
        public_key: str,
        secret_key: str
    ) -> bool:
        """
        Add UBECrc trustline to an existing Stellar account
        Useful for stewards who already have wallets
        
        Args:
            public_key: Account public key
            secret_key: Account secret key
            
        Returns:
            True if trustline added successfully
        """
        # Verify account exists
        if not await self.has_stellar_account(public_key):
            logger.error(f"Account does not exist: {public_key}")
            return False
        
        # Create trustline
        return await self._create_trustline(secret_key)
