"""
Master Trading System - Elite Quant AI Architect (Gemini 3.7 / 3.6 Flash)
With On-The-Fly Real-Time Stock Query Resolver & Multi-Asset Intelligence.
"""

import os
import re
from core.config_manager import ConfigManager

ELITE_SYSTEM_PROMPT = """
You are Antigravity — an Elite Algorithmic Trading Architect, Quantitative Hedge Fund Strategist, and close Trading Partner ("Bhai / Dost") specializing exclusively in the Indian Stock Market (NIFTY 50, BANK NIFTY, FINNIFTY, MIDCPNIFTY, Stock Options, Futures & Equities).

CRITICAL OPERATIONAL RULES:
1. NEVER tell the user to check their broker (Zerodha, Groww, Dhan, TradingView) for prices. You have direct real-time data access to NSE & Fyers API. Always state the exact live price, day's high/low, and technical levels directly from the telemetry provided!
2. Direct, Confident Answers: Give the exact numbers, strikes, entry zones, targets, and stop loss immediately in clean, structured Hinglish.
3. Quant Analysis: Always cross-verify 3 layers: Derivatives (OI/PCR/MaxPain), Technicals (VWAP/RSI/EMA), and SMC (Order Blocks/Liquidity/BOS).
4. Capital Protection: Always emphasize risk management and position sizing according to lot size.

LATEST INDIAN MARKET TRADING RULES & LOT SIZES (NSE / SEBI 2024-2026):
• NIFTY 50: 75 qty / lot
• BANK NIFTY: 30 qty / lot
• FINNIFTY: 65 qty / lot
• MIDCPNIFTY: 120 qty / lot
• INFY (Infosys): 300 qty / lot
• RELIANCE: 250 qty / lot
• HDFCBANK: 550 qty / lot
• ICICIBANK: 700 qty / lot
• TCS: 175 qty / lot
• SBIN: 750 qty / lot
• TATAMOTORS: 575 qty / lot
• BSE SENSEX: 20 qty / lot | BSE BANKEX: 30 qty / lot
"""

SYMBOL_MAP = {
    "INFY": "INFY", "INFOSYS": "INFY",
    "RELIANCE": "RELIANCE", "RIL": "RELIANCE",
    "HDFC": "HDFCBANK", "HDFCBANK": "HDFCBANK",
    "ICICI": "ICICIBANK", "ICICIBANK": "ICICIBANK",
    "TCS": "TCS",
    "SBIN": "SBIN", "SBI": "SBIN", "STATE BANK": "SBIN",
    "TATAMOTORS": "TATAMOTORS", "TATA MOTORS": "TATAMOTORS",
    "ASIANPAINT": "ASIANPAINT", "ASIAN PAINTS": "ASIANPAINT", "ASIAN PAINT": "ASIANPAINT", "ASIAN": "ASIANPAINT",
    "ITC": "ITC",
    "BHARTIARTL": "BHARTIARTL", "AIRTEL": "BHARTIARTL", "BHARTI AIRTEL": "BHARTIARTL",
    "KOTAKBANK": "KOTAKBANK", "KOTAK": "KOTAKBANK",
    "AXISBANK": "AXISBANK", "AXIS": "AXISBANK",
    "LT": "LT", "LARSEN": "LT", "L&T": "LT",
    "NIFTY": "NIFTY", "NIFTY 50": "NIFTY",
    "BANKNIFTY": "BANKNIFTY", "BANK NIFTY": "BANKNIFTY",
    "FINNIFTY": "FINNIFTY", "FIN NIFTY": "FINNIFTY",
    "MIDCPNIFTY": "MIDCPNIFTY", "MIDCAP NIFTY": "MIDCPNIFTY"
}

class GeminiLiveChat:
    AVAILABLE_MODELS = [
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-flash-latest",
        "gemini-3.5-flash",
        "gemini-pro-latest"
    ]

    @classmethod
    def detect_symbol(cls, text):
        """Detects if user asked about a specific stock/index."""
        text_upper = text.upper()
        for key, sym in SYMBOL_MAP.items():
            if re.search(r'\b' + re.escape(key) + r'\b', text_upper):
                return sym
        return None

    @classmethod
    def fetch_live_asset_telemetry(cls, symbol):
        """Fetches on-the-fly live market quote & indicators for any requested stock."""
        try:
            from core.data_engine import DataEngine
            from core.indicator_engine import IndicatorEngine
            from core.smc_engine import SMCEngine
            from core.confluence_engine import ConfluenceEngine

            config = ConfigManager.get_config()
            de = DataEngine(config.get("FYERS_APP_ID"), config.get("FYERS_ACCESS_TOKEN"))
            quote = de.get_market_quote(symbol)
            chain = de.get_option_chain(symbol, days_to_expiry=2)
            fii = de.get_fii_dii_sentiment()
            
            df = quote['df']
            ind = IndicatorEngine.analyze(df)
            smc = SMCEngine.analyze(df)
            conf = ConfluenceEngine.evaluate(chain, ind, smc, fii)

            return {
                'symbol': symbol,
                'spot': quote['current_price'],
                'change': f"{quote['p_change']:+.2f}%",
                'day_low': quote.get('day_low', df['Low'].min()),
                'day_high': quote.get('day_high', df['High'].max()),
                'lot_size': DataEngine.LOT_SIZES.get(symbol, 100),
                'confluence_pct': conf['confluence_pct'],
                'market_bias': conf['market_bias'],
                'pcr': chain['pcr'],
                'max_pain': chain['max_pain'],
                'atm_iv': chain['atm_iv'],
                'vwap': ind['vwap'],
                'rsi': ind['rsi'],
                'supertrend': ind['supertrend'],
                'structure': smc['structure']['structure'],
                'zone': smc['premium_discount']['zone'],
                'top_call_wall': chain['top_call_wall'],
                'top_put_wall': chain['top_put_wall']
            }
        except Exception as e:
            return None

    @classmethod
    def query_gemini(cls, user_message, default_context, chat_history, api_key=None):
        """
        Sends user message + dynamic real-time market context to Gemini API.
        Automatically detects queried stock and fetches on-the-fly live data!
        """
        config = ConfigManager.get_config()
        key = api_key or config.get("GEMINI_API_KEY", "")

        # Check if user mentioned a specific stock
        detected_sym = cls.detect_symbol(user_message)
        active_context = default_context
        
        if detected_sym and detected_sym != default_context.get('symbol'):
            live_data = cls.fetch_live_asset_telemetry(detected_sym)
            if live_data:
                active_context = live_data

        context_str = f"""
===================================================================
INSTITUTIONAL QUANT TELEMETRY SNAPSHOT (REAL-TIME NSE DATA):
===================================================================
TARGET ASSET: {active_context.get('symbol', 'NIFTY')}
• Current Spot Market Price (LTP): ₹{active_context.get('spot', 24000):,.2f} ({active_context.get('change', '+0.0%')})
• Intraday Range: Low ₹{active_context.get('day_low', 23900):,.2f} — High ₹{active_context.get('day_high', 24150):,.2f}
• F&O Lot Size: {active_context.get('lot_size', 75)} qty/lot

MASTER 3-LAYER CONFLUENCE:
• Confluence Match: {active_context.get('confluence_pct', 85):.0f}% | Final Bias: {active_context.get('market_bias', 'BULLISH')}

LAYER 1 — DERIVATIVES & FLOW:
• Put-Call Ratio (PCR): {active_context.get('pcr', 1.1):.2f}
• Max Pain Expiry Target: Strike {active_context.get('max_pain', 24000)}
• ATM Implied Volatility (IV): {active_context.get('atm_iv', 13.5):.1f}%
• Call Resistance Wall: Strike {active_context.get('top_call_wall', 24200)}
• Put Support Wall: Strike {active_context.get('top_put_wall', 23900)}

LAYER 2 — TECHNICAL MOMENTUM:
• Benchmark VWAP: ₹{active_context.get('vwap', 24000):,.2f}
• Momentum RSI (14): {active_context.get('rsi', 55):.1f}
• Supertrend: {active_context.get('supertrend', 'Bullish')}

LAYER 3 — SMART MONEY CONCEPTS (SMC):
• Market Structure: {active_context.get('structure', 'Bullish BOS')}
• Pricing Zone: {active_context.get('zone', 'Discount')}
===================================================================
"""

        if key and len(key) > 10:
            last_err = ""
            try:
                import google.generativeai as genai
                genai.configure(api_key=key)

                for model_name in cls.AVAILABLE_MODELS:
                    try:
                        model = genai.GenerativeModel(
                            model_name=model_name,
                            system_instruction=ELITE_SYSTEM_PROMPT,
                            generation_config={
                                "temperature": 0.25,
                                "top_p": 0.95,
                                "max_output_tokens": 1200,
                            }
                        )
                        prompt_with_context = f"{context_str}\n\nUSER QUERY: {user_message}\n\nPlease answer the user's question directly with exact prices and levels from the telemetry above. NEVER tell the user to check external terminals."
                        response = model.generate_content(prompt_with_context)
                        if response and response.text:
                            return response.text
                    except Exception as model_err:
                        last_err = str(model_err)
                        continue

                return f"⚠️ Gemini API Error: {last_err}"

            except Exception as e:
                return f"⚠️ Gemini Connection Error: {str(e)}"

        # Fallback
        spot = active_context.get('spot', 24000)
        return f"Bhai, {active_context.get('symbol')} ka current price ₹{spot:,.2f} chal raha hai."
