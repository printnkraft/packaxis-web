import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_endpoints():
    print("🧪 Testing Packaxis Packaging Canada API Endpoints\n")
    
    # Test 1: Products List
    print("1️⃣  GET /api/products/ - Products List")
    try:
        resp = requests.get(f"{BASE_URL}/products/", timeout=5)
        data = resp.json()
        print(f"   Status: {resp.status_code}")
        print(f"   Results: {data.get('count', 0)} products\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # Test 2: Cart Baskets List
    print("2️⃣  GET /api/cart/baskets/ - Cart Baskets")
    try:
        resp = requests.get(f"{BASE_URL}/cart/baskets/", timeout=5)
        print(f"   Status: {resp.status_code}")
        print(f"   Response preview: {str(resp.json())[:100]}...\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # Test 3: Shipping Rates
    print("3️⃣  GET /api/shipping/methods/ - Shipping Methods")
    try:
        resp = requests.get(f"{BASE_URL}/shipping/methods/", timeout=5)
        print(f"   Status: {resp.status_code}")
        print(f"   Results: {resp.json().get('count', 0)} methods\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # Test 4: Taxes by Province
    print("4️⃣  GET /api/taxes/ - Provincial Tax Rates")
    try:
        resp = requests.get(f"{BASE_URL}/taxes/", timeout=5)
        print(f"   Status: {resp.status_code}")
        print(f"   Results: {resp.json().get('count', 0)} provinces\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    # Test 5: Promotions
    print("5️⃣  GET /api/promotions/ - Discount Codes")
    try:
        resp = requests.get(f"{BASE_URL}/promotions/", timeout=5)
        print(f"   Status: {resp.status_code}")
        print(f"   Results: {resp.json().get('count', 0)} codes\n")
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
    
    print("✅ API Testing Complete!")

if __name__ == "__main__":
    test_endpoints()
