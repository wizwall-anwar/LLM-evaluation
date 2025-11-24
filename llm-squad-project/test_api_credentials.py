#!/usr/bin/env python3
"""
Test script to verify all API credentials are working
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai():
    """Test OpenAI API connection"""
    print("\n" + "="*60)
    print("Testing OpenAI API...")
    print("="*60)

    try:
        import openai
        api_key = os.getenv('OPENAI_API_KEY')

        if not api_key:
            print("❌ OPENAI_API_KEY not found in .env")
            return False

        client = openai.OpenAI(api_key=api_key)

        # Make a simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10
        )

        result = response.choices[0].message.content
        print(f"✅ OpenAI API is working!")
        print(f"   Response: {result}")
        return True

    except Exception as e:
        print(f"❌ OpenAI API test failed: {str(e)}")
        return False

def test_anthropic():
    """Test Anthropic API connection"""
    print("\n" + "="*60)
    print("Testing Anthropic (Claude) API...")
    print("="*60)

    try:
        import anthropic
        api_key = os.getenv('ANTHROPIC_API_KEY')

        if not api_key:
            print("❌ ANTHROPIC_API_KEY not found in .env")
            return False

        client = anthropic.Anthropic(api_key=api_key)

        # Make a simple API call
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'API test successful'"}]
        )

        result = message.content[0].text
        print(f"✅ Anthropic API is working!")
        print(f"   Response: {result}")
        return True

    except Exception as e:
        print(f"❌ Anthropic API test failed: {str(e)}")
        return False

def test_huggingface():
    """Test Hugging Face API connection"""
    print("\n" + "="*60)
    print("Testing Hugging Face API...")
    print("="*60)

    try:
        from huggingface_hub import HfApi
        api_key = os.getenv('HUGGINGFACE_API_KEY')

        if not api_key:
            print("❌ HUGGINGFACE_API_KEY not found in .env")
            return False

        api = HfApi(token=api_key)

        # Test by getting user info
        user_info = api.whoami()
        print(f"✅ Hugging Face API is working!")
        print(f"   Authenticated as: {user_info.get('name', 'Unknown')}")
        return True

    except Exception as e:
        print(f"❌ Hugging Face API test failed: {str(e)}")
        return False

def main():
    """Run all API tests"""
    print("\n" + "="*60)
    print("API CREDENTIALS TEST")
    print("="*60)

    results = {
        'OpenAI': test_openai(),
        'Anthropic': test_anthropic(),
        'Hugging Face': test_huggingface()
    }

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for service, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{service:20} {status}")

    all_passed = all(results.values())

    print("\n" + "="*60)
    if all_passed:
        print("🎉 All API credentials are working!")
    else:
        print("⚠️  Some API credentials failed. Please check the errors above.")
    print("="*60 + "\n")

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
