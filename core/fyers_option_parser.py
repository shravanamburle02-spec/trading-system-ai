"""
Master Trading System - Complete Fyers API v3 Live Option Chain Parser
Handles Live Real-Time Tick Ingestion with Dynamic Black-Scholes Greeks & OI Change for all indices & equities.
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
            strike = item.get('strike_price', item.get('strikePrice', item.get('strike', 0)))
            if strike <= 0:
                continue

            if strike not in parsed_rows:
                parsed_rows[strike] = {
                    'strike': strike,
                    'ce_ltp': 0.05, 'ce_iv': 10.0, 'ce_oi': 0, 'ce_change_oi': 0, 'ce_volume': 0, 'ce_delta': 0.5, 'ce_theta': -12.0, 'ce_gamma': 0.001, 'ce_vega': 8.0,
                    'pe_ltp': 0.05, 'pe_iv': 10.0, 'pe_oi': 0, 'pe_change_oi': 0, 'pe_volume': 0, 'pe_delta': -0.5, 'pe_theta': -12.0, 'pe_gamma': 0.001, 'pe_vega': 8.0
                }

            if 'call_market_data' in item or 'call_oi' in item or 'call' in item:
                c_data = item.get('call_market_data', item.get('call', item))
                p_data = item.get('put_market_data', item.get('put', item))

                ce_iv = float(c_data.get('iv', c_data.get('call_iv', 10.0)))
                pe_iv = float(p_data.get('iv', p_data.get('put_iv', 10.0)))

                ce_greeks = cls.calculate_greeks(spot_price, strike, T, r, ce_iv/100.0, 'CE')
                pe_greeks = cls.calculate_greeks(spot_price, strike, T, r, pe_iv/100.0, 'PE')

                parsed_rows[strike]['ce_ltp'] = float(c_data.get('ltp', c_data.get('call_ltp', parsed_rows[strike]['ce_ltp'])))
                parsed_rows[strike]['ce_oi'] = int(c_data.get('oi', c_data.get('call_oi', 0)))
                parsed_rows[strike]['ce_change_oi'] = int(c_data.get('oichng', c_data.get('oi_change', c_data.get('change_oi', 0))))
                parsed_rows[strike]['ce_volume'] = int(c_data.get('volume', c_data.get('call_volume', 0)))
                parsed_rows[strike]['ce_iv'] = ce_iv
                parsed_rows[strike]['ce_delta'] = ce_greeks['delta']
                parsed_rows[strike]['ce_theta'] = ce_greeks['theta']
                parsed_rows[strike]['ce_gamma'] = ce_greeks['gamma']
                parsed_rows[strike]['ce_vega'] = ce_greeks['vega']

                parsed_rows[strike]['pe_ltp'] = float(p_data.get('ltp', p_data.get('put_ltp', parsed_rows[strike]['pe_ltp'])))
                parsed_rows[strike]['pe_oi'] = int(p_data.get('oi', p_data.get('put_oi', 0)))
                parsed_rows[strike]['pe_change_oi'] = int(p_data.get('oichng', p_data.get('oi_change', p_data.get('change_oi', 0))))
                parsed_rows[strike]['pe_volume'] = int(p_data.get('volume', p_data.get('put_volume', 0)))
                parsed_rows[strike]['pe_iv'] = pe_iv
                parsed_rows[strike]['pe_delta'] = pe_greeks['delta']
                parsed_rows[strike]['pe_theta'] = pe_greeks['theta']
                parsed_rows[strike]['pe_gamma'] = pe_greeks['gamma']
                parsed_rows[strike]['pe_vega'] = pe_greeks['vega']

            else:
                opt_type = item.get('option_type', item.get('optionType', 'CE')).upper()
                ltp = float(item.get('ltp', item.get('lp', 0.05)))
                oi = int(item.get('oi', 0))
                oi_chg = int(item.get('oichng', item.get('oi_change', item.get('change_oi', 0))))
                vol = int(item.get('volume', item.get('v', 0)))
                iv = float(item.get('iv', 10.0))
                greeks = cls.calculate_greeks(spot_price, strike, T, r, iv/100.0, opt_type)

                if 'CE' in opt_type or 'CALL' in opt_type:
                    parsed_rows[strike]['ce_ltp'] = ltp
                    parsed_rows[strike]['ce_oi'] = oi
                    parsed_rows[strike]['ce_change_oi'] = oi_chg
                    parsed_rows[strike]['ce_volume'] = vol
                    parsed_rows[strike]['ce_iv'] = iv
                    parsed_rows[strike]['ce_delta'] = greeks['delta']
                    parsed_rows[strike]['ce_theta'] = greeks['theta']
                    parsed_rows[strike]['ce_gamma'] = greeks['gamma']
                    parsed_rows[strike]['ce_vega'] = greeks['vega']
                else:
                    parsed_rows[strike]['pe_ltp'] = ltp
                    parsed_rows[strike]['pe_oi'] = oi
                    parsed_rows[strike]['pe_change_oi'] = oi_chg
                    parsed_rows[strike]['pe_volume'] = vol
                    parsed_rows[strike]['pe_iv'] = iv
                    parsed_rows[strike]['pe_delta'] = greeks['delta']
                    parsed_rows[strike]['pe_theta'] = greeks['theta']
                    parsed_rows[strike]['pe_gamma'] = greeks['gamma']
                    parsed_rows[strike]['pe_vega'] = greeks['vega']

        if not parsed_rows:
            return None

        df = pd.DataFrame(list(parsed_rows.values()))
        df = df.sort_values(by='strike').reset_index(drop=True)
        return df
