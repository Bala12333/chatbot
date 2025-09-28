#!/usr/bin/env python3
"""
Script to help set up Google Cloud credentials
"""

import os
import shutil
from pathlib import Path

def setup_credentials():
    """Set up Google Cloud credentials"""
    
    print("🔧 Setting up Google Cloud Credentials")
    print("=" * 50)
    
    # Windows path from user
    windows_path = r"C:\Users\bala\Downloads\logical-bloom-472314-d4-3b1dc56de916.json"
    
    # Linux destination
    credentials_dir = Path("credentials")
    credentials_dir.mkdir(exist_ok=True)
    
    linux_path = credentials_dir / "google-cloud-key.json"
    
    print(f"Source (Windows): {windows_path}")
    print(f"Destination (Linux): {linux_path}")
    
    # Instructions for manual copy
    print("\n📝 Manual Setup Instructions:")
    print("=" * 50)
    print("Since you're running this in a Linux environment but your JSON key")
    print("is on Windows, you need to copy the file manually:")
    print()
    print("1. Copy this file from Windows:")
    print(f"   {windows_path}")
    print()
    print("2. Save it as:")
    print(f"   {linux_path.absolute()}")
    print()
    print("3. Or create the file content directly:")
    
    # Create a template
    template_content = """{
  "type": "service_account",
  "project_id": "logical-bloom-472314-d4",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY_HERE\\n-----END PRIVATE KEY-----\\n",
  "client_email": "your-service-account@logical-bloom-472314-d4.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "your-cert-url"
}"""
    
    with open(linux_path, 'w') as f:
        f.write(template_content)
    
    print(f"   Created template at: {linux_path}")
    print("   Edit this file with your actual Google Cloud credentials")
    print()
    
    # Update .env file
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Update the credentials path
        updated_content = content.replace(
            "C:\\Users\\bala\\Downloads\\logical-bloom-472314-d4-3b1dc56de916.json",
            str(linux_path.absolute())
        )
        
        with open(env_path, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Updated .env file with Linux path: {linux_path.absolute()}")
    
    print()
    print("🔄 After copying the credentials:")
    print("1. Restart the Django server")
    print("2. Test voice features at http://127.0.0.1:8000")
    print()
    print("🧪 Test without Google Cloud:")
    print("The chatbot already works with text chat using local knowledge!")

if __name__ == "__main__":
    setup_credentials()