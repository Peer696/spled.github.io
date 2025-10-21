#!/usr/bin/env python3
"""
Test script voor de eenvoudige versie
"""

import os
import sys
import subprocess

def test_imports():
    print("🔍 Testing imports...")
    try:
        sys.path.append('backend')
        from backend.api_simple import app, generate_answer, generate_text
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment():
    print("🔍 Testing environment variables...")
    from dotenv import load_dotenv
    load_dotenv('backend/.env')
    
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    
    if deepseek_key and supabase_url:
        print("✅ Environment variables loaded!")
        return True
    else:
        print("❌ Missing environment variables")
        print(f"DeepSeek key: {'✅' if deepseek_key else '❌'}")
        print(f"Supabase URL: {'✅' if supabase_url else '❌'}")
        return False

def test_api_connection():
    print("🔍 Testing DeepSeek API connection...")
    try:
        sys.path.append('backend')
        from backend.api_simple import generate_text
        
        response = generate_text("Hello, this is a test")
        if "API Error" not in response:
            print("✅ DeepSeek API connection successful!")
            print(f"Response: {response[:50]}...")
            return True
        else:
            print(f"❌ DeepSeek API error: {response}")
            return False
    except Exception as e:
        print(f"❌ DeepSeek API error: {e}")
        return False

def test_chat_function():
    print("🔍 Testing chat function...")
    try:
        sys.path.append('backend')
        from backend.api_simple import generate_answer
        
        # Test with sample content
        sample_content = "This is a sample PDF content about machine learning and artificial intelligence."
        response = generate_answer("What is this about?", sample_content)
        
        if response and "Please upload" not in response:
            print("✅ Chat function working!")
            print(f"Response: {response[:100]}...")
            return True
        else:
            print(f"❌ Chat function error: {response}")
            return False
    except Exception as e:
        print(f"❌ Chat function error: {e}")
        return False

def main():
    print("🚀 Testing Simple PDF Chatbot Setup...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_environment,
        test_api_connection,
        test_chat_function
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready!")
        print("\nNext steps:")
        print("1. Add your Supabase keys to .env files")
        print("2. Run: python3 backend/api_simple.py")
        print("3. In another terminal: cd frontend && npm start")
        print("\nNote: This is a demo version without real PDF processing.")
        print("For real PDF processing, you'll need to install PyMuPDF.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nTo fix:")
        print("1. Make sure your .env files have the correct keys")
        print("2. Check your internet connection for API calls")

if __name__ == "__main__":
    main()