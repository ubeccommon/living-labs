#!/usr/bin/env python3
"""
Muxed Address Verification Script - UBEC Standard v1.0
Tests the complete muxed address generation and registration flow

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from stellar_muxed import (
    StellarMuxedAccountManager,
    create_muxed,
    decode_muxed,
    verify_muxed,
    is_muxed,
    InvalidAddressError,
    InvalidDeviceIdError,
)


def test_muxed_address_generation():
    """Test basic muxed address generation"""
    print("=" * 80)
    print("TEST 1: Muxed Address Generation")
    print("=" * 80)
    
    # Test data
    steward_wallet = "GAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSUBEC"
    device1_serial = "SB2024001234"
    device2_serial = "SB2024005678"
    device3_serial = "68b11e9c48183d0008742820"  # OpenSenseMap format
    
    print(f"\nSteward Wallet: {steward_wallet}\n")
    
    # Generate muxed addresses
    try:
        muxed1 = create_muxed(steward_wallet, device1_serial)
        muxed2 = create_muxed(steward_wallet, device2_serial)
        muxed3 = create_muxed(steward_wallet, device3_serial)
        
        print(f"Device 1 ({device1_serial}):")
        print(f"  Muxed: {muxed1}")
        print(f"  Length: {len(muxed1)}")
        print(f"  Starts with M: {muxed1.startswith('M')}")
        print(f"  Is muxed format: {is_muxed(muxed1)}")
        
        print(f"\nDevice 2 ({device2_serial}):")
        print(f"  Muxed: {muxed2}")
        print(f"  Length: {len(muxed2)}")
        print(f"  Starts with M: {muxed2.startswith('M')}")
        print(f"  Is muxed format: {is_muxed(muxed2)}")
        
        print(f"\nDevice 3 ({device3_serial}):")
        print(f"  Muxed: {muxed3}")
        print(f"  Length: {len(muxed3)}")
        print(f"  Starts with M: {muxed3.startswith('M')}")
        print(f"  Is muxed format: {is_muxed(muxed3)}")
        
        # Verify uniqueness
        print("\nUniqueness Check:")
        all_unique = len({muxed1, muxed2, muxed3}) == 3
        print(f"  All muxed addresses unique: {all_unique}")
        
        # Verify they differ from base wallet
        print("\nBase Wallet Comparison:")
        print(f"  Muxed1 != Base: {muxed1 != steward_wallet}")
        print(f"  Muxed2 != Base: {muxed2 != steward_wallet}")
        print(f"  Muxed3 != Base: {muxed3 != steward_wallet}")
        
        # Verify all have correct format
        all_valid_format = all([
            len(muxed1) == 69,
            len(muxed2) == 69,
            len(muxed3) == 69,
            muxed1.startswith('M'),
            muxed2.startswith('M'),
            muxed3.startswith('M'),
            all_unique,
        ])
        
        if all_valid_format:
            print("\n✅ TEST 1 PASSED")
            return True
        else:
            print("\n❌ TEST 1 FAILED: Format validation failed")
            return False
        
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        return False


def test_muxed_address_decoding():
    """Test muxed address decoding"""
    print("\n" + "=" * 80)
    print("TEST 2: Muxed Address Decoding")
    print("=" * 80)
    
    steward_wallet = "GAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSUBEC"
    device_serial = "SB2024001234"
    
    try:
        # Generate muxed address
        muxed = create_muxed(steward_wallet, device_serial)
        
        print(f"\nOriginal:")
        print(f"  Base: {steward_wallet}")
        print(f"  Serial: {device_serial}")
        print(f"  Muxed: {muxed}")
        
        # Decode it
        base_decoded, mux_id = decode_muxed(muxed)
        
        print(f"\nDecoded:")
        print(f"  Base: {base_decoded}")
        print(f"  Mux ID: {mux_id}")
        
        # Verify
        print(f"\nVerification:")
        base_matches = base_decoded == steward_wallet
        mux_id_positive = mux_id > 0
        print(f"  Base matches: {base_matches}")
        print(f"  Mux ID is positive: {mux_id_positive}")
        
        # Test determinism - generate again and verify same result
        muxed2 = create_muxed(steward_wallet, device_serial)
        
        print(f"\nDeterminism Test:")
        is_deterministic = muxed == muxed2
        print(f"  Same serial generates same muxed: {is_deterministic}")
        
        # Test with verify function
        is_valid = verify_muxed(muxed, steward_wallet, device_serial)
        print(f"  Verify function confirms: {is_valid}")
        
        if base_matches and mux_id_positive and is_deterministic and is_valid:
            print("\n✅ TEST 2 PASSED")
            return True
        else:
            print("\n❌ TEST 2 FAILED: Validation failed")
            return False
        
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        return False


def test_invalid_inputs():
    """Test error handling with invalid inputs"""
    print("\n" + "=" * 80)
    print("TEST 3: Invalid Input Handling")
    print("=" * 80)
    
    test_cases = [
        ("Invalid address", "SB123", InvalidAddressError),
        ("TOO_SHORT", "SB123", InvalidAddressError),
        ("GAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSUBEC", "", InvalidDeviceIdError),
        ("", "SB123", InvalidAddressError),
    ]
    
    passed = 0
    failed = 0
    
    for address, serial, expected_exception in test_cases:
        try:
            muxed = create_muxed(address, serial)
            print(f"❌ Should have failed for: {address[:20] if address else '(empty)'}... / {serial if serial else '(empty)'}")
            failed += 1
        except (InvalidAddressError, InvalidDeviceIdError) as e:
            # Check if it's the expected exception type
            if isinstance(e, expected_exception):
                print(f"✅ Correctly rejected: {address[:20] if address else '(empty)'}... / {serial if serial else '(empty)'}")
                print(f"   Error: {str(e)[:50]}...")
                passed += 1
            else:
                print(f"⚠️  Wrong exception type for: {address[:20] if address else '(empty)'}... / {serial if serial else '(empty)'}")
                print(f"   Expected: {expected_exception.__name__}, Got: {type(e).__name__}")
                failed += 1
        except Exception as e:
            print(f"❌ Unexpected exception: {type(e).__name__}: {str(e)[:50]}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✅ TEST 3 PASSED")
        return True
    else:
        print("\n❌ TEST 3 FAILED")
        return False


def test_multiple_stewards():
    """Test that different stewards get different muxed addresses for same device serial"""
    print("\n" + "=" * 80)
    print("TEST 4: Multiple Stewards")
    print("=" * 80)
    
    steward1 = "GAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSUBEC"
    steward2 = "GBVOL67TMUQBGL4TZYNMY3ZQ5WGQYFPFD5VJRWXR72VA33VFNL225PL5"
    device_serial = "SB2024001234"  # Same serial for both
    
    try:
        muxed1 = create_muxed(steward1, device_serial)
        muxed2 = create_muxed(steward2, device_serial)
        
        print(f"\nSame device serial: {device_serial}")
        print(f"\nSteward 1: {steward1[:20]}...")
        print(f"  Muxed: {muxed1[:30]}...")
        
        print(f"\nSteward 2: {steward2[:20]}...")
        print(f"  Muxed: {muxed2[:30]}...")
        
        addresses_different = muxed1 != muxed2
        print(f"\nMuxed addresses are different: {addresses_different}")
        
        # Decode to verify bases
        base1, _ = decode_muxed(muxed1)
        base2, _ = decode_muxed(muxed2)
        
        base1_correct = base1 == steward1
        base2_correct = base2 == steward2
        print(f"Base 1 correct: {base1_correct}")
        print(f"Base 2 correct: {base2_correct}")
        
        # Verify each with its steward
        verify1 = verify_muxed(muxed1, steward1, device_serial)
        verify2 = verify_muxed(muxed2, steward2, device_serial)
        print(f"Muxed 1 verifies with steward 1: {verify1}")
        print(f"Muxed 2 verifies with steward 2: {verify2}")
        
        if addresses_different and base1_correct and base2_correct and verify1 and verify2:
            print("\n✅ TEST 4 PASSED")
            return True
        else:
            print("\n❌ TEST 4 FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
        return False


def test_reverse_lookup():
    """Test reverse lookup functionality"""
    print("\n" + "=" * 80)
    print("TEST 5: Reverse Lookup")
    print("=" * 80)
    
    steward = "GAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSUBEC"
    devices = {
        "SB2024001234": "School Garden",
        "SB2024005678": "Rooftop Station",
        "68b11e9c48183d0008742820": "Classroom Monitor"
    }
    
    try:
        # Create muxed addresses
        muxed_map = {}
        for device_id in devices.keys():
            muxed_map[device_id] = create_muxed(steward, device_id)
        
        # Create registry
        registry = {device_id: steward for device_id in devices.keys()}
        
        # Test reverse lookup for each device
        print(f"\nReverse Lookup Tests:")
        all_found = True
        
        for device_id, device_name in devices.items():
            muxed = muxed_map[device_id]
            found = StellarMuxedAccountManager.reverse_lookup(muxed, registry)
            
            match = found == device_id
            print(f"  {device_name}: {'✅' if match else '❌'} (expected {device_id}, found {found})")
            
            if not match:
                all_found = False
        
        if all_found:
            print("\n✅ TEST 5 PASSED")
            return True
        else:
            print("\n❌ TEST 5 FAILED: Some lookups failed")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 5 FAILED: {e}")
        return False


def test_muxed_info():
    """Test get_muxed_info functionality"""
    print("\n" + "=" * 80)
    print("TEST 6: Muxed Info Extraction")
    print("=" * 80)
    
    steward = "GAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSUBEC"
    device = "SB2024001234"
    
    try:
        muxed = create_muxed(steward, device)
        info = StellarMuxedAccountManager.get_muxed_info(muxed)
        
        print(f"\nMuxed Info:")
        print(f"  Valid: {info.is_valid}")
        print(f"  Muxed Address: {info.muxed_address[:30]}...")
        print(f"  Base Address: {info.base_address}")
        print(f"  Mux ID: {info.mux_id}")
        print(f"  Length: {info.length}")
        
        # Validate info
        checks = [
            info.is_valid,
            info.muxed_address == muxed,
            info.base_address == steward,
            info.mux_id > 0,
            info.length == 69,
        ]
        
        if all(checks):
            print("\n✅ TEST 6 PASSED")
            return True
        else:
            print("\n❌ TEST 6 FAILED: Info validation failed")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 6 FAILED: {e}")
        return False


def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total = len(results)
    passed = sum(results)
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} {'❌' if failed > 0 else ''}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Muxed address implementation is working correctly.")
        print("\nUBEC Standard v1.0 - VERIFIED AND PRODUCTION READY")
    else:
        print("\n⚠️  Some tests failed. Please review the implementation.")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("MUXED ADDRESS VERIFICATION SUITE - UBEC STANDARD v1.0")
    print("=" * 80)
    print("\nThis script verifies the muxed address generation functionality")
    print("for the UBEC Reciprocal Economy system.\n")
    
    results = []
    
    # Run all tests
    results.append(test_muxed_address_generation())
    results.append(test_muxed_address_decoding())
    results.append(test_invalid_inputs())
    results.append(test_multiple_stewards())
    results.append(test_reverse_lookup())
    results.append(test_muxed_info())
    
    # Print summary
    print_summary(results)
    
    # Return exit code
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
