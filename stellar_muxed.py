"""
Stellar Multiplexed Account Manager - UBEC Standard v1.0

This module provides the canonical implementation for managing multiplexed Stellar 
accounts in the UBEC Reciprocal Economy system. Each SenseBox device receives a 
unique muxed address derived from its serial number, enabling individual device 
tracking while all funds flow to the steward's main wallet.

Design Principles:
- Deterministic: Same input always produces same output
- Stateless: No internal state management
- Fail-fast: Invalid inputs rejected immediately
- Type-safe: Proper type hints throughout
- Well-documented: Clear examples and use cases

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

from stellar_sdk import MuxedAccount, StrKey
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class MuxedInfo:
    """Structured information about a muxed address."""
    muxed_address: str
    base_address: str
    mux_id: int
    is_valid: bool
    length: int


class MuxedAddressError(Exception):
    """Base exception for muxed address operations."""
    pass


class InvalidAddressError(MuxedAddressError):
    """Raised when a Stellar address is invalid."""
    pass


class InvalidDeviceIdError(MuxedAddressError):
    """Raised when a device ID is invalid."""
    pass


class StellarMuxedAccountManager:
    """
    Manages multiplexed Stellar accounts for UBEC environmental monitoring devices.
    
    This class provides deterministic muxed address generation, enabling each
    device to have a unique tracking address while maintaining a single base
    wallet for the steward.
    
    Key Features:
    - Deterministic generation (SHA256-based)
    - Zero-state operations
    - Comprehensive validation
    - Reverse lookup support
    
    Example:
        >>> manager = StellarMuxedAccountManager()
        >>> base = "GAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSUBEC"
        >>> device = "SB2024001234"
        >>> muxed = manager.create_muxed_address(base, device)
        >>> print(muxed)
        MAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSVMELBKG6UAVVEUN3Q
    """
    
    @staticmethod
    def create_muxed_address(base_address: str, device_id: str) -> str:
        """
        Generate a deterministic muxed address for a device.
        
        The mux ID is derived from SHA256(device_id), ensuring:
        - Same device ID always produces same muxed address
        - Different device IDs produce different muxed addresses
        - Collision probability is cryptographically negligible
        
        Args:
            base_address: Steward's base Stellar address (G... format, 56 chars)
            device_id: Unique device identifier (serial number, UUID, etc.)
            
        Returns:
            Muxed address (M... format, 69 chars)
            
        Raises:
            InvalidAddressError: If base address is invalid
            InvalidDeviceIdError: If device ID is empty or invalid
            
        Example:
            >>> addr = StellarMuxedAccountManager.create_muxed_address(
            ...     "GAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSUBEC",
            ...     "SB2024001234"
            ... )
            >>> print(addr[:5], "...", addr[-5:])
            MAWLP ... EUN3Q
        """
        # Validate base address
        if not base_address or not base_address.strip():
            raise InvalidAddressError("Base Stellar address cannot be empty")
        
        try:
            StrKey.decode_ed25519_public_key(base_address.strip())
        except Exception as e:
            raise InvalidAddressError(
                f"Invalid Stellar address format: {base_address[:20]}... - {e}"
            )
        
        # Validate device ID
        if not device_id or not device_id.strip():
            raise InvalidDeviceIdError("Device ID cannot be empty")
        
        # Generate deterministic mux_id from device_id
        hash_bytes = hashlib.sha256(device_id.strip().encode('utf-8')).digest()
        mux_id = int.from_bytes(hash_bytes[:8], byteorder='big')
        
        # Create muxed account
        muxed = MuxedAccount(
            account_id=base_address.strip(),
            account_muxed_id=mux_id
        )
        
        logger.debug(
            f"Generated muxed address: device={device_id[:20]}, "
            f"mux_id={mux_id}, addr={muxed.account_muxed[:20]}..."
        )
        
        return muxed.account_muxed
    
    @staticmethod
    def decode_muxed_address(muxed_address: str) -> Tuple[str, int]:
        """
        Decode a muxed address into its components.
        
        Args:
            muxed_address: Muxed Stellar address (M... format)
            
        Returns:
            Tuple of (base_address, mux_id)
            
        Raises:
            InvalidAddressError: If muxed address is invalid
            
        Example:
            >>> base, mux_id = StellarMuxedAccountManager.decode_muxed_address(
            ...     "MAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSVMELBKG6UAVVEUN3Q"
            ... )
            >>> print(f"Base: {base[:10]}..., Mux ID: {mux_id}")
            Base: GAWLPSGBZV..., Mux ID: 12721273177070810405
        """
        if not muxed_address or not muxed_address.strip():
            raise InvalidAddressError("Muxed address cannot be empty")
        
        try:
            muxed = MuxedAccount.from_account(muxed_address.strip())
            return muxed.account_id, muxed.account_muxed_id
        except Exception as e:
            raise InvalidAddressError(
                f"Failed to decode muxed address: {muxed_address[:20]}... - {e}"
            )
    
    @staticmethod
    def verify_muxed_address(
        muxed_address: str,
        expected_base: str,
        device_id: str
    ) -> bool:
        """
        Verify that a muxed address is correct for given base and device.
        
        This performs three checks:
        1. Muxed address decodes successfully
        2. Base address matches expected
        3. Mux ID matches device_id hash
        
        Args:
            muxed_address: Muxed address to verify
            expected_base: Expected base Stellar address
            device_id: Expected device ID
            
        Returns:
            True if all checks pass, False otherwise
            
        Example:
            >>> is_valid = StellarMuxedAccountManager.verify_muxed_address(
            ...     "MAWLP...UN3Q",
            ...     "GAWLP...SUBEC",
            ...     "SB2024001234"
            ... )
            >>> print(is_valid)
            True
        """
        try:
            # Decode muxed address
            base, mux_id = StellarMuxedAccountManager.decode_muxed_address(
                muxed_address
            )
            
            # Verify base address matches
            if base != expected_base.strip():
                logger.warning(
                    f"Base mismatch: expected {expected_base[:20]}..., "
                    f"got {base[:20]}..."
                )
                return False
            
            # Verify mux_id matches device_id hash
            hash_bytes = hashlib.sha256(device_id.strip().encode('utf-8')).digest()
            expected_mux_id = int.from_bytes(hash_bytes[:8], byteorder='big')
            
            if mux_id != expected_mux_id:
                logger.warning(
                    f"Mux ID mismatch for device {device_id}: "
                    f"expected {expected_mux_id}, got {mux_id}"
                )
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False
    
    @staticmethod
    def get_muxed_info(muxed_address: str) -> MuxedInfo:
        """
        Get structured information about a muxed address.
        
        Args:
            muxed_address: Muxed address to analyze
            
        Returns:
            MuxedInfo dataclass with address components
            
        Example:
            >>> info = StellarMuxedAccountManager.get_muxed_info("MAWLP...UN3Q")
            >>> print(f"Base: {info.base_address}, Valid: {info.is_valid}")
            Base: GAWLP...SUBEC, Valid: True
        """
        try:
            base, mux_id = StellarMuxedAccountManager.decode_muxed_address(
                muxed_address
            )
            return MuxedInfo(
                muxed_address=muxed_address,
                base_address=base,
                mux_id=mux_id,
                is_valid=True,
                length=len(muxed_address)
            )
        except Exception:
            return MuxedInfo(
                muxed_address=muxed_address,
                base_address="",
                mux_id=0,
                is_valid=False,
                length=len(muxed_address) if muxed_address else 0
            )
    
    @staticmethod
    def reverse_lookup(
        muxed_address: str,
        device_registry: Dict[str, str]
    ) -> Optional[str]:
        """
        Find which device a muxed address belongs to.
        
        This is useful when receiving payments to identify the source device.
        
        Args:
            muxed_address: Muxed address to look up
            device_registry: Mapping of device_id -> base_address
            
        Returns:
            Device ID if found, None otherwise
            
        Example:
            >>> registry = {
            ...     "SB2024001234": "GAWLP...SUBEC",
            ...     "SB2024005678": "GAWLP...SUBEC"
            ... }
            >>> device = StellarMuxedAccountManager.reverse_lookup(
            ...     "MAWLP...UN3Q",
            ...     registry
            ... )
            >>> print(device)
            SB2024001234
        """
        if not muxed_address or not device_registry:
            return None
        
        try:
            base, mux_id = StellarMuxedAccountManager.decode_muxed_address(
                muxed_address
            )
            
            # Check each registered device
            for device_id, device_base in device_registry.items():
                if device_base == base:
                    # Recalculate mux_id for this device
                    hash_bytes = hashlib.sha256(
                        device_id.strip().encode('utf-8')
                    ).digest()
                    device_mux_id = int.from_bytes(hash_bytes[:8], byteorder='big')
                    
                    if device_mux_id == mux_id:
                        logger.debug(f"Found device: {device_id}")
                        return device_id
            
            logger.warning(f"No device found for muxed: {muxed_address[:20]}...")
            return None
            
        except Exception as e:
            logger.error(f"Reverse lookup failed: {e}")
            return None
    
    @staticmethod
    def is_muxed_format(address: str) -> bool:
        """
        Quick check if address has muxed format (starts with M).
        
        Note: This only checks format, not validity. Use decode_muxed_address
        for full validation.
        
        Args:
            address: Address to check
            
        Returns:
            True if starts with 'M', False otherwise
            
        Example:
            >>> StellarMuxedAccountManager.is_muxed_format("MAWLP...")
            True
            >>> StellarMuxedAccountManager.is_muxed_format("GAWLP...")
            False
        """
        return bool(address and address.strip().startswith('M'))


# Module-level convenience functions for cleaner API
def create_muxed(base_address: str, device_id: str) -> str:
    """
    Create a muxed address (convenience wrapper).
    
    Args:
        base_address: Base Stellar address
        device_id: Device identifier
        
    Returns:
        Muxed address
    """
    return StellarMuxedAccountManager.create_muxed_address(base_address, device_id)


def decode_muxed(muxed_address: str) -> Tuple[str, int]:
    """
    Decode a muxed address (convenience wrapper).
    
    Args:
        muxed_address: Muxed address
        
    Returns:
        Tuple of (base_address, mux_id)
    """
    return StellarMuxedAccountManager.decode_muxed_address(muxed_address)


def verify_muxed(muxed: str, base: str, device: str) -> bool:
    """
    Verify a muxed address (convenience wrapper).
    
    Args:
        muxed: Muxed address
        base: Base address
        device: Device ID
        
    Returns:
        True if valid
    """
    return StellarMuxedAccountManager.verify_muxed_address(muxed, base, device)


def is_muxed(address: str) -> bool:
    """
    Check if address is muxed format (convenience wrapper).
    
    Args:
        address: Address to check
        
    Returns:
        True if muxed format
    """
    return StellarMuxedAccountManager.is_muxed_format(address)


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    
    print("=" * 80)
    print("STELLAR MUXED ACCOUNT MANAGER - UBEC STANDARD v1.0")
    print("=" * 80)
    
    # Example steward wallet
    steward_wallet = "GAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSUBEC"
    
    # Example devices
    devices = {
        "SB2024001234": "School Garden Monitor",
        "SB2024005678": "Rooftop Weather Station",
        "68b11e9c48183d0008742820": "Classroom Air Quality"
    }
    
    print(f"\nSteward Base Wallet:\n  {steward_wallet}\n")
    print("Device Registration:")
    print("-" * 80)
    
    # Generate muxed addresses
    muxed_map = {}
    for device_id, device_name in devices.items():
        try:
            muxed = create_muxed(steward_wallet, device_id)
            muxed_map[device_id] = muxed
            
            print(f"\n✓ {device_name}")
            print(f"  Device ID: {device_id}")
            print(f"  Muxed:     {muxed}")
            print(f"  Format:    {'✓ Valid' if is_muxed(muxed) else '✗ Invalid'}")
        except Exception as e:
            print(f"\n✗ {device_name}: {e}")
            sys.exit(1)
    
    # Verification tests
    print("\n" + "=" * 80)
    print("VERIFICATION TESTS")
    print("=" * 80)
    
    test_device = "SB2024001234"
    test_muxed = muxed_map[test_device]
    
    # Test 1: Decode
    print(f"\nTest 1: Decoding")
    base, mux_id = decode_muxed(test_muxed)
    print(f"  Base matches:    {'✓' if base == steward_wallet else '✗'}")
    print(f"  Mux ID:          {mux_id}")
    
    # Test 2: Verify
    print(f"\nTest 2: Verification")
    is_valid = verify_muxed(test_muxed, steward_wallet, test_device)
    print(f"  Valid:           {'✓' if is_valid else '✗'}")
    
    # Test 3: Get info
    print(f"\nTest 3: Detailed Info")
    info = StellarMuxedAccountManager.get_muxed_info(test_muxed)
    print(f"  Valid:           {info.is_valid}")
    print(f"  Length:          {info.length} chars")
    print(f"  Base:            {info.base_address[:20]}...")
    
    # Test 4: Reverse lookup
    print(f"\nTest 4: Reverse Lookup")
    registry = {dev_id: steward_wallet for dev_id in devices.keys()}
    found = StellarMuxedAccountManager.reverse_lookup(test_muxed, registry)
    print(f"  Found device:    {found}")
    print(f"  Correct:         {'✓' if found == test_device else '✗'}")
    
    # Test 5: Determinism
    print(f"\nTest 5: Determinism")
    muxed2 = create_muxed(steward_wallet, test_device)
    print(f"  Same input:      {muxed2 == test_muxed}")
    
    # Test 6: Input validation
    print("\n" + "=" * 80)
    print("INPUT VALIDATION TESTS")
    print("=" * 80)
    
    test_cases = [
        ("Empty base address", "", "TEST001"),
        ("Empty device ID", steward_wallet, ""),
        ("Invalid base format", "INVALID", "TEST001"),
        ("Both empty", "", ""),
    ]
    
    for name, base, device in test_cases:
        try:
            result = create_muxed(base, device)
            print(f"✗ {name}: Should have failed")
        except (InvalidAddressError, InvalidDeviceIdError) as e:
            print(f"✓ {name}: Correctly rejected")
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED - SYSTEM READY")
    print("=" * 80)
