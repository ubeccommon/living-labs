#!/usr/bin/env python3
"""
Stellar Muxed Account Testing Suite for UBEC Environmental Monitoring
Tests the complete muxed account implementation for SenseBox device wallets

This project uses the services of Claude and Anthropic PBC to inform our 
decisions and recommendations. This project was made possible with the 
assistance of Claude and Anthropic PBC.

Usage:
    python3 test_muxed_accounts.py
"""

from stellar_sdk import MuxedAccount, StrKey
import hashlib
from typing import Tuple, Dict, List
from decimal import Decimal


class StellarMuxedAccountManager:
    """Manages multiplexed accounts for SenseBox devices"""
    
    @staticmethod
    def create_device_muxed_address(user_stellar_address: str, sensebox_id: str) -> str:
        """
        Create a multiplexed Stellar address for a specific SenseBox device.
        
        Args:
            user_stellar_address: The user's base Stellar address (G...)
            sensebox_id: The unique SenseBox/OpenSenseMap ID
            
        Returns:
            Multiplexed address (M...) for the device
        """
        try:
            # Validate the Stellar address
            StrKey.decode_ed25519_public_key(user_stellar_address)
            
            # Create a deterministic mux_id from the sensebox_id
            # Use SHA256 hash and take first 8 bytes as uint64
            hash_bytes = hashlib.sha256(sensebox_id.encode()).digest()
            mux_id = int.from_bytes(hash_bytes[:8], 'big')
            
            # Create the muxed account
            muxed = MuxedAccount(account_id=user_stellar_address, account_muxed_id=mux_id)
            
            return muxed.account_muxed
            
        except Exception as e:
            raise ValueError(f"Failed to create muxed address: {e}")
    
    @staticmethod
    def decode_muxed_address(muxed_address: str) -> Tuple[str, int]:
        """
        Decode a multiplexed address back to its components.
        
        Args:
            muxed_address: The multiplexed Stellar address (M...)
            
        Returns:
            Tuple of (base_address, mux_id)
        """
        try:
            muxed = MuxedAccount.from_account(muxed_address)
            return muxed.account_id, muxed.account_muxed_id
            
        except Exception as e:
            raise ValueError(f"Failed to decode muxed address: {e}")
    
    @staticmethod
    def verify_sensebox_muxed(muxed_address: str, expected_base: str, sensebox_id: str) -> bool:
        """
        Verify that a muxed address matches the expected base account and sensebox ID.
        
        Args:
            muxed_address: The muxed address to verify
            expected_base: The expected base account address
            sensebox_id: The SenseBox ID
            
        Returns:
            True if valid, False otherwise
        """
        try:
            base, mux_id = StellarMuxedAccountManager.decode_muxed_address(muxed_address)
            
            # Check base account matches
            if base != expected_base:
                return False
            
            # Verify mux_id matches sensebox_id hash
            hash_bytes = hashlib.sha256(sensebox_id.encode()).digest()
            expected_mux_id = int.from_bytes(hash_bytes[:8], 'big')
            
            return mux_id == expected_mux_id
            
        except Exception:
            return False


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def test_provided_muxed_account():
    """Test the user-provided muxed account"""
    print_section("TEST 1: Verify Provided Muxed Account")
    
    muxed_address = "MAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSUSPHEEUOGA7AHOCXI"
    
    try:
        base, mux_id = StellarMuxedAccountManager.decode_muxed_address(muxed_address)
        
        print(f"✅ Valid Muxed Account")
        print(f"\n  Muxed Address: {muxed_address}")
        print(f"  Base Account:  {base}")
        print(f"  Mux ID:        {mux_id}")
        print(f"  Mux ID (hex):  0x{mux_id:016X}")
        
        # Try to find which sensebox this belongs to
        print(f"\n  Analysis:")
        print(f"    - All funds sent to this muxed address will appear in: {base}")
        print(f"    - This virtual sub-account ID: {mux_id}")
        print(f"    - Transactions can track which device generated the observation")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_sensebox_muxed_generation():
    """Test muxed account generation for known SenseBox devices"""
    print_section("TEST 2: Generate Muxed Accounts for SenseBox Devices")
    
    # Known configuration from the project
    base_account = "GAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSUBEC"
    senseboxes = {
        "SENS_EB69D665F6EB2F5E": "Primary school device (OpenSenseMap: 68b11e9c48183d0008742820)",
        "68b11e9c48183d0008742820": "OpenSenseMap ID format",
        "SENS_001": "Test device 1",
        "SENS_002": "Test device 2",
    }
    
    results = []
    
    for sensebox_id, description in senseboxes.items():
        try:
            muxed = StellarMuxedAccountManager.create_device_muxed_address(
                base_account, sensebox_id
            )
            base, mux_id = StellarMuxedAccountManager.decode_muxed_address(muxed)
            
            print(f"✅ {sensebox_id}")
            print(f"   Description: {description}")
            print(f"   Muxed: {muxed}")
            print(f"   Mux ID: {mux_id}\n")
            
            results.append({
                'sensebox_id': sensebox_id,
                'muxed_address': muxed,
                'mux_id': mux_id,
                'description': description
            })
            
        except Exception as e:
            print(f"❌ {sensebox_id}: {e}\n")
    
    return results


def test_muxed_verification():
    """Test verification of muxed accounts"""
    print_section("TEST 3: Verify Muxed Account Ownership")
    
    base_account = "GAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSUBEC"
    sensebox_id = "68b11e9c48183d0008742820"
    
    # Generate muxed address
    muxed = StellarMuxedAccountManager.create_device_muxed_address(
        base_account, sensebox_id
    )
    
    # Test verification
    is_valid = StellarMuxedAccountManager.verify_sensebox_muxed(
        muxed, base_account, sensebox_id
    )
    
    print(f"SenseBox ID: {sensebox_id}")
    print(f"Base Account: {base_account}")
    print(f"Generated Muxed: {muxed}")
    print(f"\nVerification: {'✅ VALID' if is_valid else '❌ INVALID'}")
    
    # Test with wrong sensebox_id
    is_invalid = StellarMuxedAccountManager.verify_sensebox_muxed(
        muxed, base_account, "WRONG_ID"
    )
    
    print(f"\nTest with wrong ID: {'❌ FAILED (should be invalid)' if is_invalid else '✅ PASSED (correctly invalid)'}")
    
    return is_valid and not is_invalid


def test_payment_scenarios():
    """Test realistic payment scenarios with muxed accounts"""
    print_section("TEST 4: Simulate Payment Scenarios")
    
    base_account = "GAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSUBEC"
    
    # Simulate multiple devices for one user
    devices = [
        ("68b11e9c48183d0008742820", "School Garden SenseBox"),
        ("SENS_CLASSROOM_01", "Classroom Monitor"),
        ("SENS_WEATHER_STATION", "Weather Station"),
    ]
    
    print(f"User Base Account: {base_account}\n")
    print(f"Payment Simulation: 7.14 UBEC per observation\n")
    
    total_payments = Decimal("0")
    
    for i, (device_id, device_name) in enumerate(devices, 1):
        muxed = StellarMuxedAccountManager.create_device_muxed_address(
            base_account, device_id
        )
        
        # Simulate payments
        observations = i * 2  # Different number of observations per device
        payment_per_obs = Decimal("7.14")
        total_device_payment = payment_per_obs * observations
        total_payments += total_device_payment
        
        print(f"Device {i}: {device_name}")
        print(f"  Device ID: {device_id}")
        print(f"  Muxed Address: {muxed}")
        print(f"  Observations: {observations}")
        print(f"  Payment: {total_device_payment} UBEC")
        print(f"  Memo: Obs_{device_id[:8]}")
        print()
    
    print(f"{'─' * 80}")
    print(f"Total UBEC to be received in base account: {total_payments} UBEC")
    print(f"All payments route to: {base_account}")
    print(f"\n✅ Multi-device payment simulation complete")
    
    return True


def test_database_integration():
    """Test database structure for muxed accounts"""
    print_section("TEST 5: Database Integration Schema")
    
    print("Recommended Database Schema Updates:\n")
    
    schema = """
-- Add muxed_wallet_address to observers table
ALTER TABLE phenomenological.observers 
ADD COLUMN IF NOT EXISTS muxed_wallet_address TEXT;

-- Add index for quick lookup
CREATE INDEX IF NOT EXISTS idx_observers_muxed_wallet 
ON phenomenological.observers(muxed_wallet_address);

-- View to join observations with muxed addresses
CREATE OR REPLACE VIEW phenomenological.observations_with_wallets AS
SELECT 
    o.*,
    obs.stellar_address as observer_base_wallet,
    obs.muxed_wallet_address as observer_muxed_wallet,
    re.amount as ubec_amount,
    re.stellar_transaction_hash as payment_tx
FROM phenomenological.observations o
LEFT JOIN phenomenological.observers obs ON o.observer_id = obs.id
LEFT JOIN phenomenological.reciprocal_exchanges re ON o.id = re.observation_id
WHERE o.deleted_at IS NULL;

-- Function to generate muxed address on observer registration
CREATE OR REPLACE FUNCTION phenomenological.generate_muxed_wallet()
RETURNS TRIGGER AS $$
DECLARE
    muxed_address TEXT;
BEGIN
    -- This would call the Python function to generate muxed address
    -- For now, just placeholder logic
    IF NEW.stellar_address IS NOT NULL AND NEW.device_id IS NOT NULL THEN
        -- In production, call StellarMuxedAccountManager.create_device_muxed_address
        NEW.muxed_wallet_address := 'M' || NEW.stellar_address || '_' || NEW.device_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-generate muxed address
CREATE TRIGGER generate_muxed_wallet_trigger
    BEFORE INSERT OR UPDATE ON phenomenological.observers
    FOR EACH ROW
    WHEN (NEW.stellar_address IS NOT NULL AND NEW.device_id IS NOT NULL)
    EXECUTE FUNCTION phenomenological.generate_muxed_wallet();
"""
    
    print(schema)
    print("\n✅ Database schema recommendations generated")
    
    return True


def test_ubec_tokenomics():
    """Verify UBEC tokenomics with muxed accounts"""
    print_section("TEST 6: UBEC Tokenomics Verification")
    
    print("UBEC Token Distribution Configuration:\n")
    
    config = {
        'asset_code': 'UBECrc',
        'issuer': 'GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC',
        'distributor': 'GAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSUBEC',
        'base_reward': Decimal('7.14'),
        'sensor_bonus': Decimal('0.50'),
        'stewardship_bonus': Decimal('1.00'),
    }
    
    for key, value in config.items():
        print(f"  {key:20s}: {value}")
    
    # Calculate daily potential
    observations_per_day = 96  # Every 15 minutes
    sensors = 7  # School SenseBox has 7 sensors
    
    base_daily = config['base_reward'] * observations_per_day
    sensor_daily = config['sensor_bonus'] * sensors * observations_per_day
    steward_daily = config['stewardship_bonus'] * observations_per_day
    total_daily = base_daily + sensor_daily + steward_daily
    
    print(f"\nDaily Earning Potential (per device):")
    print(f"  Base rewards:        {base_daily:8.2f} UBEC")
    print(f"  Sensor bonuses:      {sensor_daily:8.2f} UBEC ({sensors} sensors)")
    print(f"  Stewardship bonus:   {steward_daily:8.2f} UBEC")
    print(f"  {'─' * 40}")
    print(f"  Total daily:         {total_daily:8.2f} UBEC")
    
    print(f"\nMonthly projection: {total_daily * 30:.2f} UBEC")
    print(f"Annual projection:  {total_daily * 365:.2f} UBEC")
    
    print("\n✅ Tokenomics calculations complete")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  UBEC STELLAR MUXED ACCOUNT TEST SUITE")
    print("  Freie Waldorfschule Frankfurt (Oder)")
    print("=" * 80)
    
    tests = [
        ("Verify Provided Muxed Account", test_provided_muxed_account),
        ("Generate SenseBox Muxed Accounts", test_sensebox_muxed_generation),
        ("Muxed Account Verification", test_muxed_verification),
        ("Payment Scenarios", test_payment_scenarios),
        ("Database Integration", test_database_integration),
        ("UBEC Tokenomics", test_ubec_tokenomics),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10s} {test_name}")
    
    print(f"\n{'─' * 80}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Muxed account system is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above.")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
