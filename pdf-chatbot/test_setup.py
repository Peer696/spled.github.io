#!/usr/bin/env python3
"""
Test script om te controleren of alles werkt
"""

import os
import sys
import subprocess

def test_imports():
    print("🔍 Testing imports...")
    try:
        import fastapi
        import uvicorn
        import numpy
        import sklearn
        import tensorflow_hub
        import fitz
        import openai
        from supabase import create_client
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment():
    print("🔍 Testing environment variables...")
    from dotenv import load_dotenv
    load_dotenv()
    
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if deepseek_key and supabase_url:
        print("✅ Environment variables loaded!")
        return True
    else:
        print("❌ Missing environment variables")
        print(f"DeepSeek key: {'✅' if deepseek_key else '❌'}")
        print(f"Supabase URL: {'✅' if supabase_url else '❌'}")
        print(f"Supabase Key: {'✅' if supabase_key else '❌'}")
        return False

def test_api_connection():
    print("🔍 Testing DeepSeek API connection...")
    try:
        import openai
        from dotenv import load_dotenv
        load_dotenv()
        
        client = openai.OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"content": "Hello, this is a test", "role": "user"}],
            max_tokens=10
        )
        
        print("✅ DeepSeek API connection successful!")
        return True
    except Exception as e:
        print(f"❌ DeepSeek API error: {e}")
        return False

def main():
    print("🚀 Testing PDF Chatbot Setup...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_environment,
        test_api_connection
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
        print("2. Run: python api.py")
        print("3. In another terminal: cd frontend && npm start")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nTo fix:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Add your Supabase keys to .env files")

if __name__ == "__main__":
    main()