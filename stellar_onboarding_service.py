#!/usr/bin/env python3
"""
Stellar Onboarding Service
Creates and funds new Stellar wallets for users who don't have one

Handles:
- Keypair generation
- Account funding via Create Account operation
- UBECrc trustline creation
- Funding account balance monitoring

Design Principles Applied:
- Principle #5: Strict async operations throughout
- Principle #9: Integrated rate limiting
- Principle #10: Clear separation of concerns
- Principle #12: Method singularity - no duplication

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

import logging
import asyncio
import aiohttp
from typing import Dict, Optional
from decimal import Decimal
from stellar_sdk import (
    Keypair,
    Server,
    TransactionBuilder,
    Network,
    Asset,
    Account
)
from stellar_sdk.exceptions import NotFoundError, BadRequestError

logger = logging.getLogger(__name__)


class StellarOnboardingService:
    """
    Service for onboarding new users to the Stellar network
    
    Creates wallets, funds them, and adds UBECrc trustlines automatically
    """
    
    # Constants
    FUNDING_AMOUNT = Decimal("5.5")  # XLM to fund new accounts with
    TRUSTLINE_RESERVE = Decimal("0.5")  # Extra XLM for trustline reserve
    RATE_LIMIT_DELAY = 0.5  # Seconds between operations
    
    def __init__(
        self,
        stellar_service,
        funding_account_public: str,
        funding_account_secret: str,
        ubecrc_asset_code: str,
        ubecrc_issuer: str,
        min_funding_amount: float = 5.5,
        database = None
    ):
        """
        Initialize the onboarding service
        
        Args:
            stellar_service: Main stellar service instance
            funding_account_public: Public key of account that funds new wallets
            funding_account_secret: Secret key of funding account
            ubecrc_asset_code: Asset code for UBECrc token
            ubecrc_issuer: Issuer public key for UBECrc
            min_funding_amount: Minimum XLM to fund accounts with
            database: Database connection for logging (optional)
        """
        self.stellar_service = stellar_service
        self.funding_public = funding_account_public
        self.funding_secret = funding_account_secret
        self.ubecrc_asset_code = ubecrc_asset_code
        self.ubecrc_issuer = ubecrc_issuer
        self.min_funding_amount = Decimal(str(min_funding_amount))
        self.database = database
        
        # Get Stellar network info from service
        self.horizon_url = stellar_service.horizon_url if stellar_service else "https://horizon.stellar.org"
        self.network = stellar_service.network if stellar_service else "public"
        
        # Determine network passphrase
        if self.network == "testnet":
            self.network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE
        else:
            self.network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE
        
        # Rate limiting
        self._rate_limit_semaphore = asyncio.Semaphore(2)  # Max 2 concurrent ops
        
        logger.info(f"Stellar Onboarding Service initialized")
        logger.info(f"  Network: {self.network}")
        logger.info(f"  Funding account: {self.funding_public[:8]}...")
        logger.info(f"  Min funding: {self.min_funding_amount} XLM")
    
    async def create_and_fund_account(
        self,
        steward_email: str,
        steward_name: str
    ) -> Optional[Dict]:
        """
        Complete workflow to create and fund a new Stellar wallet
        
        Steps:
        1. Generate new keypair
        2. Fund account with Create Account operation
        3. Add UBECrc trustline
        4. Log creation in database (if available)
        
        Args:
            steward_email: Email of the steward (for logging)
            steward_name: Name of the steward (for logging)
            
        Returns:
            Dict with wallet info or None if failed:
            {
                'success': True,
                'public_key': 'G...',
                'secret_key': 'S...',
                'funded': True,
                'trustline_created': True,
                'xlm_balance': 5.5,
                'network': 'public',
                'steward_email': '...',
                'steward_name': '...'
            }
        """
        try:
            logger.info(f"Creating wallet for {steward_name} ({steward_email})")
            
            # Step 1: Generate keypair
            new_keypair = Keypair.random()
            public_key = new_keypair.public_key
            secret_key = new_keypair.secret
            
            logger.info(f"  Generated keypair: {public_key[:8]}...")
            
            # Step 2: Fund the account
            funded = await self._fund_new_account(public_key)
            
            if not funded:
                logger.error("Failed to fund account")
                return {
                    'success': False,
                    'error': 'Failed to fund account',
                    'public_key': public_key,
                    'secret_key': secret_key
                }
            
            logger.info(f"  ✓ Account funded with {self.min_funding_amount} XLM")
            
            # Small delay to let the network process
            await asyncio.sleep(1)
            
            # Step 3: Add UBECrc trustline
            trustline_success = await self._create_trustline(secret_key)
            
            if trustline_success:
                logger.info(f"  ✓ UBECrc trustline added")
            else:
                logger.warning(f"  ⚠ UBECrc trustline failed (can add later)")
            
            # Step 4: Get final account info
            account_info = await self._get_account_info(public_key)
            
            # Step 5: Log to database if available
            if self.database:
                try:
                    await self._log_wallet_creation(
                        public_key=public_key,
                        steward_email=steward_email,
                        steward_name=steward_name,
                        xlm_funded=float(self.min_funding_amount),
                        trustline_created=trustline_success
                    )
                except Exception as e:
                    logger.warning(f"Failed to log wallet creation: {e}")
            
            return {
                'success': True,
                'public_key': public_key,
                'secret_key': secret_key,
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
        Fund a new account with minimum XLM using Create Account operation
        
        Args:
            destination_public: Public key of account to fund
            
        Returns:
            True if funding successful
        """
        try:
            async with self._rate_limit_semaphore:
                # Create funding keypair
                funding_keypair = Keypair.from_secret(self.funding_secret)
                
                # Get source account info for sequence number
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
                
                # Build Create Account transaction
                transaction = (
                    TransactionBuilder(
                        source_account=source_account,
                        network_passphrase=self.network_passphrase,
                        base_fee=100
                    )
                    .append_create_account_op(
                        destination=destination_public,
                        starting_balance=str(self.min_funding_amount)
                    )
                    .set_timeout(30)
                    .build()
                )
                
                # Sign and submit
                transaction.sign(funding_keypair)
                
                # Submit to Horizon
                server = Server(horizon_url=self.horizon_url)
                response = server.submit_transaction(transaction)
                
                if response.get('successful'):
                    logger.info(f"✓ Account created and funded: {destination_public[:8]}...")
                    return True
                else:
                    logger.error(f"Transaction failed: {response}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error funding account: {e}", exc_info=True)
            return False
    
    async def _create_trustline(self, account_secret: str) -> bool:
        """
        Add UBECrc trustline to an account
        
        Args:
            account_secret: Secret key of account to add trustline to
            
        Returns:
            True if trustline added successfully
        """
        try:
            async with self._rate_limit_semaphore:
                # Create account keypair
                account_keypair = Keypair.from_secret(account_secret)
                public_key = account_keypair.public_key
                
                # Get account info for sequence number
                account_info = await self._get_account_info(public_key)
                if not account_info:
                    logger.error("Account not found for trustline")
                    return False
                
                # Create source account object
                source_account = Account(
                    public_key,
                    int(account_info['sequence'])
                )
                
                # Create UBECrc asset
                ubecrc_asset = Asset(self.ubecrc_asset_code, self.ubecrc_issuer)
                
                # Build Change Trust transaction
                transaction = (
                    TransactionBuilder(
                        source_account=source_account,
                        network_passphrase=self.network_passphrase,
                        base_fee=100
                    )
                    .append_change_trust_op(
                        asset=ubecrc_asset,
                        limit="922337203685.4775807"  # Maximum limit
                    )
                    .set_timeout(30)
                    .build()
                )
                
                # Sign and submit
                transaction.sign(account_keypair)
                
                # Submit to Horizon
                server = Server(horizon_url=self.horizon_url)
                response = server.submit_transaction(transaction)
                
                if response.get('successful'):
                    logger.info(f"✓ Trustline added for {public_key[:8]}...")
                    return True
                else:
                    logger.error(f"Trustline transaction failed: {response}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error creating trustline: {e}", exc_info=True)
            return False
    
    async def _get_account_info(self, public_key: str) -> Optional[Dict]:
        """
        Get account information from Stellar network
        
        Args:
            public_key: Public key to query
            
        Returns:
            Account data dict or None if not found
        """
        try:
            url = f"{self.horizon_url}/accounts/{public_key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def _get_xlm_balance(self, account_info: Optional[Dict]) -> float:
        """
        Extract XLM balance from account info
        
        Args:
            account_info: Account data from Horizon
            
        Returns:
            XLM balance as float
        """
        if not account_info:
            return 0.0
        
        for balance in account_info.get('balances', []):
            if balance.get('asset_type') == 'native':
                return float(balance.get('balance', 0))
        
        return 0.0
    
    async def check_funding_capacity(self) -> Dict:
        """
        Check how many accounts can be created with current funding balance
        
        Returns:
            Dict with capacity info:
            {
                'xlm_balance': 100.0,
                'funding_amount_per_account': 5.5,
                'wallets_can_create': 18,
                'warning': 'Low balance...' or None
            }
        """
        try:
            # Get funding account info
            account_info = await self._get_account_info(self.funding_public)
            
            if not account_info:
                return {
                    'configured': False,
                    'error': 'Funding account not found'
                }
            
            xlm_balance = Decimal(str(self._get_xlm_balance(account_info)))
            
            # Calculate how many accounts can be created
            # Account for network fees and minimum balance
            usable_balance = xlm_balance - Decimal("2.0")  # Keep 2 XLM reserve
            wallets_can_create = int(usable_balance / self.min_funding_amount)
            
            # Generate warning if low
            warning = None
            if wallets_can_create < 10:
                warning = f"Low funding balance: only {wallets_can_create} accounts can be created"
            if wallets_can_create < 5:
                warning = f"CRITICAL: Only {wallets_can_create} accounts can be created. Please add XLM!"
            
            return {
                'configured': True,
                'xlm_balance': float(xlm_balance),
                'funding_amount_per_account': float(self.min_funding_amount),
                'wallets_can_create': wallets_can_create,
                'warning': warning
            }
            
        except Exception as e:
            logger.error(f"Error checking funding capacity: {e}", exc_info=True)
            return {
                'configured': True,
                'error': str(e)
            }
    
    async def has_stellar_account(self, public_key: str) -> bool:
        """
        Check if a Stellar account exists
        
        Args:
            public_key: Public key to check
            
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
    
    async def _log_wallet_creation(
        self,
        public_key: str,
        steward_email: str,
        steward_name: str,
        xlm_funded: float,
        trustline_created: bool
    ):
        """
        Log wallet creation to database
        
        Args:
            public_key: Created wallet public key
            steward_email: Steward email
            steward_name: Steward name
            xlm_funded: Amount of XLM funded
            trustline_created: Whether trustline was successful
        """
        if not self.database:
            return
        
        try:
            # This assumes a wallet_creations table exists
            # Create it if needed in your migration
            query = """
                INSERT INTO phenomenological.wallet_creations
                (public_key, steward_email, steward_name, xlm_funded, trustline_created, network)
                VALUES ($1, $2, $3, $4, $5, $6)
            """
            
            async with self.database.pool.acquire() as conn:
                await conn.execute(
                    query,
                    public_key,
                    steward_email,
                    steward_name,
                    xlm_funded,
                    trustline_created,
                    self.network
                )
            
            logger.info(f"Logged wallet creation for {steward_email}")
            
        except Exception as e:
            logger.warning(f"Failed to log wallet creation: {e}")
    
    async def close(self):
        """Cleanup resources"""
        # Nothing to cleanup currently
        pass


"""
Attribution: This project uses the services of Claude and Anthropic PBC
to inform our decisions and recommendations. This project was made
possible with the assistance of Claude and Anthropic PBC.
"""
