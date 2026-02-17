"""Test script to verify the implementation."""
import sys
from models import CreativeParams, CreativeType, ChannelType, ALL_CITIES
from generator import DisclaimerGenerator


def test_single_mode():
    """Test single city mode."""
    print("Testing single city mode...")

    generator = DisclaimerGenerator()

    params = CreativeParams(
        creative_type=CreativeType.PROMO_CODE,
        city="москва",
        channel=ChannelType.OTHER,
        end_date="31.12.24",
        discount_size=20,
        discount_unit="%",
        first_order_only=True,
        min_order_amount=1000
    )

    try:
        disclaimer = generator.generate(params)
        print(f"✅ Single mode works!")
        print(f"Disclaimer: {disclaimer[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Single mode failed: {e}")
        return False


def test_multiple_mode():
    """Test multiple cities mode."""
    print("\nTesting multiple cities mode...")

    generator = DisclaimerGenerator()

    # Test with 3 cities
    test_cities = ["москва", "мо", "тула"]

    params = CreativeParams(
        creative_type=CreativeType.PROMO_CODE,
        cities=test_cities,
        channel=ChannelType.OTHER,
        end_date="31.12.24",
        discount_size=20,
        discount_unit="%",
        first_order_only=True,
        min_order_amount=1000
    )

    try:
        disclaimers = generator.generate_multiple(params)
        print(f"✅ Multiple mode works!")
        print(f"Generated {len(disclaimers)} disclaimers")

        # Test file formatting
        file_content = generator.format_multiple_to_file(disclaimers)
        print(f"✅ File formatting works!")
        print(f"File content length: {len(file_content)} characters")
        print("\nFirst 200 characters of file:")
        print(file_content[:200])

        return True
    except Exception as e:
        print(f"❌ Multiple mode failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation():
    """Test validation logic."""
    print("\nTesting validation...")

    generator = DisclaimerGenerator()

    # Should fail - no city or cities
    try:
        params = CreativeParams(
            creative_type=CreativeType.PROMO_CODE,
            channel=ChannelType.OTHER,
            end_date="31.12.24"
        )
        print("❌ Validation failed - should require city or cities")
        return False
    except ValueError as e:
        print(f"✅ Validation works - caught: {e}")

    # Should fail - both city and cities
    try:
        params = CreativeParams(
            creative_type=CreativeType.PROMO_CODE,
            city="москва",
            cities=["москва", "тула"],
            channel=ChannelType.OTHER,
            end_date="31.12.24"
        )
        print("❌ Validation failed - should not allow both city and cities")
        return False
    except ValueError as e:
        print(f"✅ Validation works - caught: {e}")

    return True


def test_all_cities():
    """Test generation for all cities."""
    print(f"\nTesting generation for all {len(ALL_CITIES)} cities...")

    generator = DisclaimerGenerator()

    params = CreativeParams(
        creative_type=CreativeType.IMAGE,
        cities=ALL_CITIES,
        channel=ChannelType.OTHER
    )

    try:
        disclaimers = generator.generate_multiple(params)
        print(f"✅ Generated for all {len(disclaimers)} cities!")

        file_content = generator.format_multiple_to_file(disclaimers)
        print(f"✅ File size: {len(file_content)} bytes")

        return True
    except Exception as e:
        print(f"❌ All cities test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING DISCLAIMER BOT IMPLEMENTATION")
    print("=" * 60)

    results = []

    results.append(("Single Mode", test_single_mode()))
    results.append(("Multiple Mode", test_multiple_mode()))
    results.append(("Validation", test_validation()))
    results.append(("All Cities", test_all_cities()))

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20s}: {status}")

    all_passed = all(r[1] for r in results)

    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
