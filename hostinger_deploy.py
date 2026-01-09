#!/usr/bin/env python3
"""
Hostinger Deployment Script for Face Swap AI
Run this to verify your deployment setup
"""

import os
import sys

def check_deployment():
    """Check if all required files are present for Hostinger deployment"""
    
    required_files = [
        'app.py',
        'wsgi.py', 
        '.htaccess',
        'requirements.txt',
        '.env',
        'templates/index.html',
        'templates/admin.html',
        'templates/admin_login.html',
        'static/'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    print("🚀 Face Swap AI - Hostinger Deployment Check")
    print("=" * 50)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present!")
        
    # Check environment variables
    print("\n🔧 Environment Check:")
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY=' in content:
                print("✅ GEMINI_API_KEY configured")
            else:
                print("❌ GEMINI_API_KEY missing in .env")
    else:
        print("❌ .env file not found")
    
    print("\n📁 Deployment ready for Hostinger!")
    print("Upload all files to public_html directory")
    
    return True

if __name__ == "__main__":
    check_deployment()
