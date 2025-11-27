"""
Test Chatbot Integration
Verifies that the RAG chatbot is properly integrated
"""
import requests
import sys

def test_rag_backend():
    """Test if RAG backend is running"""
    print("🧪 Testing RAG Backend (port 5001)...")
    try:
        response = requests.get("http://localhost:5001", timeout=5)
        if response.status_code == 200:
            print("   ✅ RAG backend is running")
            return True
        else:
            print(f"   ⚠️ RAG backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ RAG backend not running on port 5001")
        print("   💡 Start it with: cd rag_document_search-main && python app.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_main_backend():
    """Test if main Flask app is running"""
    print("\n🧪 Testing Main Backend (port 5000)...")
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code in [200, 500]:  # 500 ok if React not built
            print("   ✅ Main backend is running")
            return True
        else:
            print(f"   ⚠️ Main backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Main backend not running on port 5000")
        print("   💡 Start it with: python flask_app.py")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_chatbot_endpoint():
    """Test the /chatbot/ask endpoint"""
    print("\n🧪 Testing Chatbot Endpoint...")
    try:
        response = requests.post(
            "http://localhost:5000/chatbot/ask",
            json={"message": "What is diabetes?", "agentic": True},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'answer' in data:
                print("   ✅ Chatbot endpoint working")
                print(f"   📝 Sample response: {data['answer'][:100]}...")
                return True
            else:
                print("   ⚠️ Response missing 'answer' field")
                return False
        else:
            print(f"   ❌ Endpoint returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to main backend")
        return False
    except requests.exceptions.Timeout:
        print("   ⚠️ Request timed out (RAG backend might be processing)")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_chatbot_health():
    """Test the /chatbot/health endpoint"""
    print("\n🧪 Testing Chatbot Health Check...")
    try:
        response = requests.get("http://localhost:5000/chatbot/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print("   ✅ Chatbot health check passed")
                return True
            else:
                print("   ⚠️ Chatbot health check shows issues")
                print(f"   📊 Status: {data}")
                return False
        else:
            print(f"   ❌ Health check returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print("")
    print("=" * 60)
    print("  🧪 Chatbot Integration Test Suite")
    print("=" * 60)
    print("")
    
    tests = [
        ("RAG Backend", test_rag_backend),
        ("Main Backend", test_main_backend),
        ("Chatbot Health", test_chatbot_health),
        ("Chatbot Endpoint", test_chatbot_endpoint),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("  📊 Test Results Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {name}")
    
    print("")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("🎉 All tests passed! Your chatbot is ready to use.")
        print("💬 Look for the 🩺 icon in the bottom-right corner of your website!")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\n💡 Quick Start Guide:")
        print("   1. Start RAG backend: cd rag_document_search-main && python app.py")
        print("   2. Start main app: python flask_app.py")
        print("   3. Open http://localhost:5000")
        return 1


if __name__ == "__main__":
    sys.exit(main())
