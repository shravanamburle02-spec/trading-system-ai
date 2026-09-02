"""
Master Trading System - Fyers API v3 Adapter
Full Symbol Mapping for NIFTY, BANKNIFTY, SENSEX, FINNIFTY, MIDCPNIFTY and Top Equities.
"""

import datetime
import pandas as pd
import numpy as np

class FyersAdapter:
    FYERS_SYMBOLS = {
        'NIFTY': 'NSE:NIFTY50-INDEX',
        'BANKNIFTY': 'NSE:NIFTYBANK-INDEX',
        'FINNIFTY': 'NSE:FINNIFTY-INDEX',
        'MIDCPNIFTY': 'NSE:MIDCPNIFTY-INDEX',
        'SENSEX': 'BSE:SENSEX-INDEX',
        'RELIANCE': 'NSE:RELIANCE-EQ',
        'HDFCBANK': 'NSE:HDFCBANK-EQ',
        'ICICIBANK': 'NSE:ICICIBANK-EQ',
        'INFY': 'NSE:INFY-EQ',
        'TCS': 'NSE:TCS-EQ',
        'SBIN': 'NSE:SBIN-EQ',
        'TATAMOTORS': 'NSE:TATAMOTORS-EQ',
        'ASIANPAINT': 'NSE:ASIANPAINT-EQ',
        'ITC': 'NSE:ITC-EQ',
        'BHARTIARTL': 'NSE:BHARTIARTL-EQ',
        'KOTAKBANK': 'NSE:KOTAKBANK-EQ',
        'AXISBANK': 'NSE:AXISBANK-EQ',
        'LT': 'NSE:LT-EQ'
    }

    def __init__(self, client_id=None, access_token=None):
        self.client_id = client_id
        self.access_token = access_token
        self.fyers_model = None
        if client_id and access_token:
            self._init_client()

    def _init_client(self):
        try:
            from fyers_apiv3 import fyersModel
            self.fyers_model = fyersModel.FyersModel(
                client_id=self.client_id,
                token=self.access_token,
                is_async=False,
                log_path=""
            )
        except Exception:
            self.fyers_model = None

    def is_connected(self):
        return self.fyers_model is not None and bool(self.access_token)

    def get_quote(self, symbol="NIFTY"):
        """Fetches real-time quotes using Fyers API v3."""
        if not self.is_connected():
            return None

        fyers_sym = self.FYERS_SYMBOLS.get(symbol.upper(), 'NSE:NIFTY50-INDEX')
        try:
            data = {"symbols": fyers_sym}
            response = self.fyers_model.quotes(data=data)
            if response.get("s") == "ok" and response.get("d"):
                quote_data = response["d"][0]["v"]
                lp = float(quote_data.get("lp", 0.0))
                prev_close = float(quote_data.get("prev_close_price", lp))
                ch = float(quote_data.get("ch", lp - prev_close))
                chp = float(quote_data.get("chp", 0.0))
                high = float(quote_data.get("high_price", lp))
                low = float(quote_data.get("low_price", lp))

                return {
                    'symbol': symbol,
                    'current_price': round(lp, 2),
                    'change': round(ch, 2),
                    'p_change': round(chp, 2),
                    'day_high': round(high, 2),
                    'day_low': round(low, 2)
                }
        except Exception:
            return None
        return None

    def get_option_chain(self, symbol="NIFTY", strikecount=30):
        """Fetches 100% Real-Time Live Option Chain via Fyers API v3."""
        if not self.is_connected():
            return None

        fyers_sym = self.FYERS_SYMBOLS.get(symbol.upper(), 'NSE:NIFTY50-INDEX')
        try:
            data = {
                "symbol": fyers_sym,
                "strikecount": strikecount
            }
            response = self.fyers_model.optionchain(data=data)
            if response.get("s") == "ok" and response.get("data"):
                return response["data"]
        except Exception:
            return None
        return None

    def get_history(self, symbol="NIFTY", resolution="5", days=5):
        """Fetches historical intraday candles using Fyers API v3."""
        if not self.is_connected():
            return None

        fyers_sym = self.FYERS_SYMBOLS.get(symbol.upper(), 'NSE:NIFTY50-INDEX')
        try:
            to_date = datetime.date.today().strftime('%Y-%m-%d')
            from_date = (datetime.date.today() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
            
            data = {
                "symbol": fyers_sym,
                "resolution": resolution,
                "date_format": "1",
                "range_from": from_date,
                "range_to": to_date,
                "cont_flag": "1"
            }
            response = self.fyers_model.history(data=data)
            if response.get("s") == "ok" and response.get("candles"):
                candles = response["candles"]
                df = pd.DataFrame(candles, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                df.set_index('datetime', inplace=True)
                return df
        except Exception:
            return None
        return None
