#!/usr/bin/env python3
"""
Stellar Onboarding Service
Creates and funds new Stellar wallets for users who don't have one

Handles:
- Keypair generation
- Account funding via Create Account operation
- UBECrc trustline creation
- Funding account balance monitoring
- Wallet attribution via immutable transaction memos
- Searchable metadata for wallet discovery

Two-Layer Metadata Strategy:
- Layer 1: Immutable transaction memo (permanent proof)
- Layer 2: Account data entries (searchable, user-modifiable)

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
from datetime import datetime  # ADDED: For metadata timestamps
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
        2. Fund account with Create Account operation (with immutable memo)
        3. Add searchable metadata to account (UBEC attribution)
        4. Add UBECrc trustline
        5. Log creation in database (if available)
        
        The wallet is marked with:
        - Immutable memo in creation transaction (permanent proof)
        - Searchable data entries on account (convenient discovery)
        
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
                'steward_name': '...',
                'creation_transaction': 'hash...',  # NEW
                'immutable_memo': 'UBEC:v1:20251006',  # NEW
                'metadata_added': True  # NEW
            }
        """
        try:
            logger.info(f"Creating wallet for {steward_name} ({steward_email})")
            
            # Step 1: Generate keypair
            new_keypair = Keypair.random()
            public_key = new_keypair.public_key
            secret_key = new_keypair.secret
            
            logger.info(f"  Generated keypair: {public_key[:8]}...")
            
            # Step 2: Fund the account (with immutable memo)
            fund_result = await self._fund_new_account(public_key)
            
            if not fund_result['success']:
                logger.error("Failed to fund account")
                return {
                    'success': False,
                    'error': fund_result.get('error', 'Failed to fund account'),
                    'public_key': public_key,
                    'secret_key': secret_key
                }
            
            creation_tx_hash = fund_result['transaction_hash']
            immutable_memo = fund_result['memo']
            
            logger.info(f"  ✓ Account funded with {self.min_funding_amount} XLM")
            logger.info(f"  ✓ Immutable memo: {immutable_memo}")
            
            # Step 2.5: Add searchable metadata (ADDED)
            metadata_added = await self._add_wallet_metadata(
                Keypair.from_secret(secret_key),
                creation_tx_hash
            )
            
            if metadata_added:
                logger.info(f"  ✓ Metadata entries added")
            else:
                logger.warning(f"  ⚠ Metadata entries failed (not critical)")
            
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
                'network': self.network,
                'creation_transaction': creation_tx_hash,  # ADDED
                'immutable_memo': immutable_memo,          # ADDED
                'metadata_added': metadata_added            # ADDED
            }
            
        except Exception as e:
            logger.error(f"Onboarding failed: {e}", exc_info=True)
            return None
    
    async def _fund_new_account(self, destination_public: str) -> dict:
        """
        Fund a new account with minimum XLM using Create Account operation
        Embeds immutable creator tag in transaction memo
        
        Args:
            destination_public: Public key of account to fund
            
        Returns:
            Dict with funding result:
            {
                'success': bool,
                'transaction_hash': str,
                'memo': str
            }
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
                            return {'success': False, 'error': 'Cannot access funding account'}
                        account_data = await response.json()
                
                # Create source account object
                source_account = Account(
                    self.funding_public,
                    int(account_data['sequence'])
                )
                
                # ADDED: Generate immutable memo tag for permanent attribution
                date_tag = datetime.utcnow().strftime("%Y%m%d")
                memo_text = f"UBEC:v1:{date_tag}"
                
                logger.info(f"    Creating with memo: {memo_text}")
                
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
                    .add_text_memo(memo_text)  # ADDED: Immutable creator tag
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
                    # CHANGED: Return dict with transaction details
                    return {
                        'success': True,
                        'transaction_hash': response['hash'],
                        'memo': memo_text
                    }
                else:
                    logger.error(f"Transaction failed: {response}")
                    return {'success': False, 'error': 'Transaction failed'}
                    
        except Exception as e:
            logger.error(f"Error funding account: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    async def _add_wallet_metadata(
        self,
        account_keypair: Keypair,
        creation_tx_hash: str
    ) -> bool:
        """
        Add searchable metadata to newly created wallet
        
        ADDED: New method for two-layer metadata strategy.
        Adds data entries that can be queried but also modified by user.
        Links back to immutable creation transaction for verification.
        
        Args:
            account_keypair: Keypair of the newly created account
            creation_tx_hash: Hash of the account creation transaction
            
        Returns:
            True if metadata successfully added
        """
        try:
            # Wait for account to settle on network
            await asyncio.sleep(2)
            
            # Get account info for sequence number
            public_key = account_keypair.public_key
            url = f"{self.horizon_url}/accounts/{public_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error("New account not found for metadata")
                        return False
                    account_data = await response.json()
            
            # Create source account object
            source_account = Account(
                public_key,
                int(account_data['sequence'])
            )
            
            # Prepare metadata values
            timestamp = datetime.utcnow().isoformat()
            project_id = "waldorfschule-frankfurt-oder"
            
            # Build metadata transaction
            transaction = (
                TransactionBuilder(
                    source_account=source_account,
                    network_passphrase=self.network_passphrase,
                    base_fee=100
                )
                .append_manage_data_op(
                    data_name="ubec:creator",
                    data_value="ubec-onboarding-v1"
                )
                .append_manage_data_op(
                    data_name="ubec:created",
                    data_value=timestamp[:64]  # Max 64 bytes
                )
                .append_manage_data_op(
                    data_name="ubec:project",
                    data_value=project_id[:64]
                )
                .append_manage_data_op(
                    data_name="ubec:creation_tx",
                    data_value=creation_tx_hash[:64]
                )
                .append_manage_data_op(
                    data_name="ubec:version",
                    data_value="1.0"
                )
                .set_timeout(30)
                .build()
            )
            
            # Sign with new account's keypair
            transaction.sign(account_keypair)
            
            # Submit transaction
            server = Server(horizon_url=self.horizon_url)
            response = server.submit_transaction(transaction)
            
            if response.get('successful'):
                logger.info(f"    ✓ Metadata added: {response['hash'][:8]}...")
                return True
            else:
                logger.error(f"Metadata transaction failed: {response}")
                return False
            
        except Exception as e:
            logger.error(f"Metadata addition failed: {e}")
            # Don't fail the whole process if metadata fails
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
    
    async def verify_wallet_origin(self, public_key: str) -> dict:
        """
        Verify if a wallet was created by our onboarding system
        
        ADDED: New method to check wallet attribution.
        Checks both current data entries and creation transaction memo.
        Even if user deletes data entries, creation memo proves origin.
        
        Args:
            public_key: Stellar public key to verify
            
        Returns:
            Dict with verification results:
            {
                'verified': bool,
                'has_metadata_entries': bool,
                'has_creation_memo': bool,
                'creation_memo': str,
                'metadata': dict
            }
        """
        try:
            # Check current account data entries
            url = f"{self.horizon_url}/accounts/{public_key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return {
                            'verified': False,
                            'error': 'Account not found'
                        }
                    account_data = await response.json()
            
            # Extract UBEC metadata entries
            data_entries = account_data.get('data', {})
            ubec_metadata = {
                k: v.get('value', '') 
                for k, v in data_entries.items() 
                if k.startswith('ubec:')
            }
            
            has_metadata = bool(ubec_metadata)
            
            # Get creation transaction to verify memo
            tx_url = f"{self.horizon_url}/accounts/{public_key}/transactions"
            tx_params = {'order': 'asc', 'limit': 1}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(tx_url, params=tx_params) as response:
                    if response.status == 200:
                        tx_data = await response.json()
                        records = tx_data.get('_embedded', {}).get('records', [])
                        if records:
                            creation_tx = records[0]
                            creation_memo = creation_tx.get('memo', '')
                            has_creation_memo = creation_memo.startswith('UBEC:')
                        else:
                            creation_memo = ''
                            has_creation_memo = False
                    else:
                        creation_memo = ''
                        has_creation_memo = False
            
            # Wallet is verified if either check passes
            verified = has_metadata or has_creation_memo
            
            return {
                'verified': verified,
                'has_metadata_entries': has_metadata,
                'has_creation_memo': has_creation_memo,
                'creation_memo': creation_memo,
                'metadata': ubec_metadata
            }
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return {
                'verified': False,
                'error': str(e)
            }
    
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
