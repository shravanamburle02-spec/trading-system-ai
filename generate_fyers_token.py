"""
Fyers API v3 Token Generator Utility
Generates Daily Access Token from App ID & Secret ID and saves to .env
"""

import os
import re
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("FYERS_APP_ID", "")
SECRET_ID = os.getenv("FYERS_SECRET_ID", "")
REDIRECT_URI = os.getenv("FYERS_REDIRECT_URI", "https://trade.fyers.in/api-login/")

def get_auth_url(app_id, secret_id, redirect_uri):
    try:
        from fyers_apiv3 import fyersModel
        session = fyersModel.SessionModel(
            client_id=app_id,
            secret_key=secret_id,
            redirect_uri=redirect_uri,
            response_type="code",
            grant_type="authorization_code"
        )
        return session.generate_authcode(), session
    except Exception as e:
        return None, None

def generate_and_save_token(session, auth_code, env_path=".env"):
    try:
        session.set_token(auth_code)
        response = session.generate_token()
        if "access_token" in response:
            access_token = response["access_token"]
            
            # Save to .env
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if "FYERS_ACCESS_TOKEN=" in content:
                    content = re.sub(r"FYERS_ACCESS_TOKEN=.*", f"FYERS_ACCESS_TOKEN={access_token}", content)
                else:
                    content += f"\nFYERS_ACCESS_TOKEN={access_token}"
                    
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(content)
            
            return True, access_token
        return False, response.get("message", "Failed to generate token")
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    print("==================================================")
    print("       FYERS API V3 DAILY ACCESS TOKEN GENERATOR   ")
    print("==================================================")
    if not APP_ID or "YOUR_" in APP_ID:
        print("❌ Error: Pehle .env file me FYERS_APP_ID aur FYERS_SECRET_ID save karo.")
    else:
        url, session = get_auth_url(APP_ID, SECRET_ID, REDIRECT_URI)
        print(f"\n1. Is Auth URL ko apne browser me open karo aur login karo:\n\n{url}\n")
        auth_code_url = input("2. Login ke baad redirect hone par browser ka pura URL yahan paste karo: ")
        
        # Extract auth_code from URL
        match = re.search(r"auth_code=([^&]+)", auth_code_url)
        auth_code = match.group(1) if match else auth_code_url.strip()
        
        success, token_or_err = generate_and_save_token(session, auth_code)
        if success:
            print(f"\n✅ SUCCESS! Access Token generate ho kar .env file me save ho gaya!")
        else:
            print(f"\n❌ Error: {token_or_err}")
