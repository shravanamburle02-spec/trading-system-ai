"""
Master Trading System - Persistent Configuration Manager
Ensures API Keys (Fyers, Gemini) are permanently stored and never reset on browser refresh.
"""

import os
import json
import re

CONFIG_FILE = "config.json"
ENV_FILE = ".env"

DEFAULT_CONFIG = {
    "FYERS_APP_ID": "2O4CWNTG7T-100",
    "FYERS_SECRET_ID": "5NAJDN8GG9",
    "FYERS_REDIRECT_URI": "https://trade.fyers.in/api-login/",
    "FYERS_ACCESS_TOKEN": "",
    "GEMINI_API_KEY": "AQ.Ab8RN6IpAXUBwBWoRCIp9FpMfgz5mxZlWsJ5AFdpXAWhFhtl6w"
}

class ConfigManager:
    @classmethod
    def get_config(cls):
        """Reads config from config.json with fallback to defaults."""
        config = DEFAULT_CONFIG.copy()
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    config.update(saved)
            except Exception:
                pass
        return config

    @classmethod
    def save_config(cls, new_config):
        """Saves config permanently to both config.json and .env."""
        config = cls.get_config()
        config.update(new_config)
        
        # Save to config.json
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass

        # Save to .env
        try:
            env_text = f"""# Master Trading System Auto-Config
FYERS_APP_ID={config.get('FYERS_APP_ID', '')}
FYERS_SECRET_ID={config.get('FYERS_SECRET_ID', '')}
FYERS_REDIRECT_URI={config.get('FYERS_REDIRECT_URI', 'https://trade.fyers.in/api-login/')}
FYERS_ACCESS_TOKEN={config.get('FYERS_ACCESS_TOKEN', '')}
GEMINI_API_KEY={config.get('GEMINI_API_KEY', '')}
"""
            with open(ENV_FILE, "w", encoding="utf-8") as f:
                f.write(env_text)
        except Exception:
            pass

        return config
