#!/usr/bin/env python3
"""
Startup Test - Verifies all dependencies load correctly
Runs before Flask app starts to catch import errors early
"""
import sys
import os

def test_imports():
    """Test critical imports"""
    print("🔍 Testing imports...")
    
    try:
        print("  ✓ Flask")
        import flask
        print("  ✓ Flask-CORS")
        from flask_cors import CORS
        print("  ✓ NumPy")
        import numpy
        print("  ✓ Scikit-learn")
        import sklearn
        print("  ✓ Pickle (built-in)")
        import pickle
        print("  ✓ Pandas")
        import pandas
        print("  ✓ Matplotlib")
        import matplotlib
        print("  ✓ Requests")
        import requests
        print("  ✓ Python-dotenv")
        import dotenv
        print("  ✓ ReportLab")
        import reportlab
        print("  ✓ Bcrypt")
        import bcrypt
        print("  ✓ Pytz")
        import pytz
        
        # Optional imports (don't fail if missing)
        try:
            print("  ✓ LangChain")
            import langchain
        except ImportError:
            print("  ⚠ LangChain (optional)")
        
        try:
            print("  ✓ Groq")
            import groq
        except ImportError:
            print("  ⚠ Groq (optional)")
        
        try:
            print("  ✓ Firebase Admin")
            import firebase_admin
        except ImportError:
            print("  ⚠ Firebase Admin (optional)")
        
        print("✅ All critical imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_files():
    """Test critical files exist"""
    print("\n🔍 Testing files...")
    
    files = [
        'flask_app.py',
        'requirements.txt',
        'firebase_config.py',
        'auth.py'
    ]
    
    all_exist = True
    for file in files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ❌ {file} NOT FOUND")
            all_exist = False
    
    # Check artifacts (not critical)
    if os.path.exists('artifacts'):
        print(f"  ✓ artifacts/ directory")
        if os.path.exists('artifacts/model.pkl'):
            print(f"  ✓ artifacts/model.pkl")
        if os.path.exists('artifacts/scaler.pkl'):
            print(f"  ✓ artifacts/scaler.pkl")
    else:
        print(f"  ⚠ artifacts/ directory (optional)")
    
    return all_exist

def test_environment():
    """Test environment variables"""
    print("\n🔍 Testing environment...")
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"  Python version: {python_version}")
    
    if sys.version_info < (3, 9):
        print(f"  ⚠ Python 3.9+ recommended")
    else:
        print(f"  ✓ Python version OK")
    
    # Check critical env vars (don't fail if missing)
    env_vars = [
        'GROQ_API_KEY',
        'FIREBASE_DATABASE_URL',
        'PINECONE_API_KEY'
    ]
    
    for var in env_vars:
        if os.getenv(var):
            print(f"  ✓ {var} set")
        else:
            print(f"  ⚠ {var} not set (optional)")
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Diabetes Predictor - Startup Test")
    print("=" * 60)
    
    success = True
    
    success = test_imports() and success
    success = test_files() and success
    success = test_environment() and success
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All startup tests PASSED")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ Some startup tests FAILED")
        print("=" * 60)
        sys.exit(1)
