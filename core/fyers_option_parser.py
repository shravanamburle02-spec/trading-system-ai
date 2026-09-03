"""
Master Trading System - Robust Fyers API v3 Live Option Chain Parser
Extracts exact real-time LTP, OI, OI Change, Volume, IV and calculates Black-Scholes Greeks
for NIFTY, BANKNIFTY, FINNIFTY, SENSEX, MIDCPNIFTY and Equities.
"""

import math
import datetime
import pandas as pd
import numpy as np
from scipy.stats import norm

class FyersOptionChainParser:
    @staticmethod
    def calculate_greeks(S, K, T, r, sigma, option_type='CE'):
        T = max(0.0005, T)
        sigma = max(0.01, sigma)
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        pdf_d1 = norm.pdf(d1)
        sqrt_T = math.sqrt(T)

        gamma = pdf_d1 / (S * sigma * sqrt_T)
        vega = (S * pdf_d1 * sqrt_T) / 100.0

        if option_type.upper() in ['CE', 'CALL']:
            delta = norm.cdf(d1)
            theta = (- (S * pdf_d1 * sigma) / (2 * sqrt_T) - r * K * math.exp(-r * T) * norm.cdf(d2)) / 365.0
        else:
            delta = norm.cdf(d1) - 1.0
            theta = (- (S * pdf_d1 * sigma) / (2 * sqrt_T) + r * K * math.exp(-r * T) * norm.cdf(-d2)) / 365.0

        return {
            'delta': round(float(delta), 2),
            'gamma': round(float(gamma), 5),
            'theta': round(float(theta), 2),
            'vega': round(float(vega), 2)
        }

    @staticmethod
    def _extract_val(data_dict, keys, default=0):
        """Safely extracts value across possible Fyers API keys."""
        if not isinstance(data_dict, dict):
            return default
        for k in keys:
            if k in data_dict and data_dict[k] is not None:
                try:
                    return type(default)(data_dict[k])
                except (ValueError, TypeError):
                    pass
        return default

    @classmethod
    def parse_fyers_response(cls, fyers_raw_data, spot_price, dte=6):
        """
        Parses Fyers API v3 Option Chain payload into standardized DataFrame with exact Black-Scholes Greeks and OI Change.
        """
        if not fyers_raw_data:
            return None

        chain_list = fyers_raw_data.get('optionsChain', fyers_raw_data.get('data', []))
        if not chain_list:
            return None

        parsed_rows = {}
        T = max(0.001, dte / 365.0)
        r = 0.065

        for item in chain_list:
            strike = cls._extract_val(item, ['strike_price', 'strikePrice', 'strike', 'strk'], 0)
            if strike <= 0:
                continue

            if strike not in parsed_rows:
                parsed_rows[strike] = {
                    'strike': strike,
                    'ce_ltp': 0.05, 'ce_iv': 10.0, 'ce_oi': 0, 'ce_change_oi': 0, 'ce_volume': 0,
                    'ce_delta': 0.5, 'ce_theta': -12.0, 'ce_gamma': 0.001, 'ce_vega': 8.0,
                    'pe_ltp': 0.05, 'pe_iv': 10.0, 'pe_oi': 0, 'pe_change_oi': 0, 'pe_volume': 0,
                    'pe_delta': -0.5, 'pe_theta': -12.0, 'pe_gamma': 0.001, 'pe_vega': 8.0
                }

            # Nested market data format (Standard Fyers v3 Option Chain API)
            if 'call_market_data' in item or 'put_market_data' in item:
                c_data = item.get('call_market_data', {})
                p_data = item.get('put_market_data', {})

                ce_iv = cls._extract_val(c_data, ['iv', 'call_iv', 'implied_volatility'], 10.0)
                pe_iv = cls._extract_val(p_data, ['iv', 'put_iv', 'implied_volatility'], 10.0)

                ce_greeks = cls.calculate_greeks(spot_price, strike, T, r, ce_iv/100.0, 'CE')
                pe_greeks = cls.calculate_greeks(spot_price, strike, T, r, pe_iv/100.0, 'PE')

                ce_oi = cls._extract_val(c_data, ['oi', 'open_interest', 'call_oi'], 0)
                ce_oich = cls._extract_val(c_data, ['oich', 'oichng', 'oi_change', 'change_oi', 'call_oi_change'], 0)
                ce_vol = cls._extract_val(c_data, ['volume', 'v', 'call_volume', 'vol'], 0)
                ce_ltp = cls._extract_val(c_data, ['ltp', 'lp', 'call_ltp', 'close'], 0.05)

                pe_oi = cls._extract_val(p_data, ['oi', 'open_interest', 'put_oi'], 0)
                pe_oich = cls._extract_val(p_data, ['oich', 'oichng', 'oi_change', 'change_oi', 'put_oi_change'], 0)
                pe_vol = cls._extract_val(p_data, ['volume', 'v', 'put_volume', 'vol'], 0)
                pe_ltp = cls._extract_val(p_data, ['ltp', 'lp', 'put_ltp', 'close'], 0.05)

                parsed_rows[strike]['ce_ltp'] = round(max(0.05, ce_ltp), 2)
                parsed_rows[strike]['ce_oi'] = ce_oi
                parsed_rows[strike]['ce_change_oi'] = ce_oich
                parsed_rows[strike]['ce_volume'] = ce_vol
                parsed_rows[strike]['ce_iv'] = round(ce_iv, 2)
                parsed_rows[strike]['ce_delta'] = ce_greeks['delta']
                parsed_rows[strike]['ce_theta'] = ce_greeks['theta']
                parsed_rows[strike]['ce_gamma'] = ce_greeks['gamma']
                parsed_rows[strike]['ce_vega'] = ce_greeks['vega']

                parsed_rows[strike]['pe_ltp'] = round(max(0.05, pe_ltp), 2)
                parsed_rows[strike]['pe_oi'] = pe_oi
                parsed_rows[strike]['pe_change_oi'] = pe_oich
                parsed_rows[strike]['pe_volume'] = pe_vol
                parsed_rows[strike]['pe_iv'] = round(pe_iv, 2)
                parsed_rows[strike]['pe_delta'] = pe_greeks['delta']
                parsed_rows[strike]['pe_theta'] = pe_greeks['theta']
                parsed_rows[strike]['pe_gamma'] = pe_greeks['gamma']
                parsed_rows[strike]['pe_vega'] = pe_greeks['vega']

            # Flat dictionary list format
            else:
                opt_type = str(item.get('option_type', item.get('optionType', item.get('symbol', 'CE')))).upper()
                ltp = cls._extract_val(item, ['ltp', 'lp', 'close'], 0.05)
                oi = cls._extract_val(item, ['oi', 'open_interest'], 0)
                oi_chg = cls._extract_val(item, ['oich', 'oichng', 'oi_change', 'change_oi'], 0)
                vol = cls._extract_val(item, ['volume', 'v', 'vol'], 0)
                iv = cls._extract_val(item, ['iv', 'implied_volatility'], 10.0)
                greeks = cls.calculate_greeks(spot_price, strike, T, r, iv/100.0, 'CE' if 'CE' in opt_type else 'PE')

                if 'CE' in opt_type or 'CALL' in opt_type:
                    parsed_rows[strike]['ce_ltp'] = round(max(0.05, ltp), 2)
                    parsed_rows[strike]['ce_oi'] = oi
                    parsed_rows[strike]['ce_change_oi'] = oi_chg
                    parsed_rows[strike]['ce_volume'] = vol
                    parsed_rows[strike]['ce_iv'] = round(iv, 2)
                    parsed_rows[strike]['ce_delta'] = greeks['delta']
                    parsed_rows[strike]['ce_theta'] = greeks['theta']
                    parsed_rows[strike]['ce_gamma'] = greeks['gamma']
                    parsed_rows[strike]['ce_vega'] = greeks['vega']
                else:
                    parsed_rows[strike]['pe_ltp'] = round(max(0.05, ltp), 2)
                    parsed_rows[strike]['pe_oi'] = oi
                    parsed_rows[strike]['pe_change_oi'] = oi_chg
                    parsed_rows[strike]['pe_volume'] = vol
                    parsed_rows[strike]['pe_iv'] = round(iv, 2)
                    parsed_rows[strike]['pe_delta'] = greeks['delta']
                    parsed_rows[strike]['pe_theta'] = greeks['theta']
                    parsed_rows[strike]['pe_gamma'] = greeks['gamma']
                    parsed_rows[strike]['pe_vega'] = greeks['vega']

        if not parsed_rows:
            return None

        df = pd.DataFrame(list(parsed_rows.values()))
        df = df.sort_values(by='strike').reset_index(drop=True)
        return df
