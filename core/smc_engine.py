"""
Master Trading System - Smart Money Concepts (SMC) Engine
Detects Market Structure (BOS / CHoCH), Institutional Order Blocks (OB),
Fair Value Gaps (FVG), Liquidity Sweeps (BSL/SSL), and Premium vs Discount Zones.
"""

import numpy as np
import pandas as pd

class SMCEngine:
    @staticmethod
    def identify_swings(df, window=3):
        """Identifies Swing Highs and Swing Lows using fractal lookback."""
        df = df.copy()
        highs = df['High'].values
        lows = df['Low'].values
        n = len(df)

        swing_highs = []
        swing_lows = []

        for i in range(window, n - window):
            # Swing High
            if all(highs[i] >= highs[i - j] for j in range(1, window + 1)) and \
               all(highs[i] > highs[i + j] for j in range(1, window + 1)):
                swing_highs.append({
                    'index': i,
                    'price': round(float(highs[i]), 2),
                    'time': df.index[i]
                })

            # Swing Low
            if all(lows[i] <= lows[i - j] for j in range(1, window + 1)) and \
               all(lows[i] < lows[i + j] for j in range(1, window + 1)):
                swing_lows.append({
                    'index': i,
                    'price': round(float(lows[i]), 2),
                    'time': df.index[i]
                })

        return swing_highs, swing_lows

    @staticmethod
    def detect_market_structure(df, swing_highs, swing_lows):
        """Detects Break of Structure (BOS) and Change of Character (CHoCH)."""
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return {'structure': 'Ranging', 'last_event': 'Neutral Range', 'trend': 'Neutral'}

        last_high = swing_highs[-1]['price']
        prev_high = swing_highs[-2]['price']
        last_low = swing_lows[-1]['price']
        prev_low = swing_lows[-2]['price']

        current_close = df['Close'].iloc[-1]

        # Check Trend
        if last_high > prev_high and last_low > prev_low:
            trend = 'Bullish Uptrend (HH + HL)'
            if current_close > last_high:
                structure = 'Bullish BOS (Continuation)'
                last_event = 'Bullish Break of Structure'
            elif current_close < last_low:
                structure = 'Bearish CHoCH (Reversal Alert)'
                last_event = 'Bearish Change of Character'
            else:
                structure = 'Bullish Consolidation'
                last_event = 'Inside Higher Low Zone'
        elif last_high < prev_high and last_low < prev_low:
            trend = 'Bearish Downtrend (LH + LL)'
            if current_close < last_low:
                structure = 'Bearish BOS (Continuation)'
                last_event = 'Bearish Break of Structure'
            elif current_close > last_high:
                structure = 'Bullish CHoCH (Reversal Alert)'
                last_event = 'Bullish Change of Character'
            else:
                structure = 'Bearish Consolidation'
                last_event = 'Inside Lower High Zone'
        else:
            trend = 'Sideways / Neutral'
            structure = 'Equilibrium Range'
            last_event = 'Building Liquidity in Range'

        return {
            'trend': trend,
            'structure': structure,
            'last_event': last_event,
            'last_swing_high': last_high,
            'last_swing_low': last_low
        }

    @staticmethod
    def detect_order_blocks(df, lookback=30):
        """Identifies institutional Demand and Supply Order Blocks (OB)."""
        sub = df.iloc[-lookback:].copy()
        bullish_obs = []
        bearish_obs = []

        current_price = df['Close'].iloc[-1]

        for i in range(2, len(sub) - 1):
            c0_open = sub['Open'].iloc[i-1]
            c0_close = sub['Close'].iloc[i-1]
            c0_low = sub['Low'].iloc[i-1]
            c0_high = sub['High'].iloc[i-1]

            c1_open = sub['Open'].iloc[i]
            c1_close = sub['Close'].iloc[i]
            c1_high = sub['High'].iloc[i]
            c1_low = sub['Low'].iloc[i]

            body_impulse = abs(c1_close - c1_open)
            avg_body = abs(sub['Close'] - sub['Open']).mean()

            # Bullish Order Block: Down candle (Red) followed by massive Green expansion
            if c0_close < c0_open and c1_close > c1_open and body_impulse > 1.8 * avg_body:
                ob_bottom = c0_low
                ob_top = c0_high
                # Check if mitigated
                future_lows = sub['Low'].iloc[i+1:]
                mitigated = any(future_lows <= ob_top) if len(future_lows) > 0 else False
                
                bullish_obs.append({
                    'type': 'Bullish Demand OB',
                    'top': round(float(ob_top), 2),
                    'bottom': round(float(ob_bottom), 2),
                    'mitigated': mitigated,
                    'status': 'Mitigated' if mitigated else 'Fresh (High Probability)',
                    'distance_pct': round(((current_price - ob_top) / current_price) * 100, 2)
                })

            # Bearish Order Block: Up candle (Green) followed by massive Red expansion
            if c0_close > c0_open and c1_close < c1_open and body_impulse > 1.8 * avg_body:
                ob_top = c0_high
                ob_bottom = c0_low
                # Check if mitigated
                future_highs = sub['High'].iloc[i+1:]
                mitigated = any(future_highs >= ob_bottom) if len(future_highs) > 0 else False

                bearish_obs.append({
                    'type': 'Bearish Supply OB',
                    'top': round(float(ob_top), 2),
                    'bottom': round(float(ob_bottom), 2),
                    'mitigated': mitigated,
                    'status': 'Mitigated' if mitigated else 'Fresh (High Probability)',
                    'distance_pct': round(((ob_bottom - current_price) / current_price) * 100, 2)
                })

        return bullish_obs[-2:], bearish_obs[-2:]

    @staticmethod
    def detect_fair_value_gaps(df, lookback=25):
        """Detects 3-candle Fair Value Gaps (FVG) / Price Imbalances."""
        sub = df.iloc[-lookback:].copy()
        fvgs = []
        current_price = df['Close'].iloc[-1]

        for i in range(len(sub) - 3):
            c1_high = sub['High'].iloc[i]
            c1_low = sub['Low'].iloc[i]

            c3_high = sub['High'].iloc[i+2]
            c3_low = sub['Low'].iloc[i+2]

            # Bullish FVG (Imbalance between C1 High and C3 Low)
            if c3_low > c1_high:
                gap_size = c3_low - c1_high
                if gap_size > (current_price * 0.0008):  # Significant gap
                    fvgs.append({
                        'type': 'Bullish FVG (Demand Gap)',
                        'top': round(float(c3_low), 2),
                        'bottom': round(float(c1_high), 2),
                        'size': round(float(gap_size), 2),
                        'active': current_price >= c1_high
                    })

            # Bearish FVG (Imbalance between C1 Low and C3 High)
            if c3_high < c1_low:
                gap_size = c1_low - c3_high
                if gap_size > (current_price * 0.0008):
                    fvgs.append({
                        'type': 'Bearish FVG (Supply Gap)',
                        'top': round(float(c1_low), 2),
                        'bottom': round(float(c3_high), 2),
                        'size': round(float(gap_size), 2),
                        'active': current_price <= c1_low
                    })

        return fvgs[-3:]

    @staticmethod
    def detect_liquidity_sweeps(df, swing_highs, swing_lows):
        """Identifies Buy-side (BSL) and Sell-side (SSL) Liquidity Sweeps / Traps."""
        if not swing_highs or not swing_lows:
            return 'No Liquidity Sweep Detected'

        last_high = swing_highs[-1]['price']
        last_low = swing_lows[-1]['price']

        recent_candle = df.iloc[-1]
        c_high = recent_candle['High']
        c_low = recent_candle['Low']
        c_close = recent_candle['Close']

        # BSL Sweep: High broke previous swing high, but close is below it (Bull Trap)
        if c_high > last_high and c_close < last_high:
            return f"🚨 BSL Sweep (Buy-Side Liquidity Hunt at {last_high}) - Bearish Trap Alert"

        # SSL Sweep: Low broke previous swing low, but close is above it (Bear Trap)
        if c_low < last_low and c_close > last_low:
            return f"🚨 SSL Sweep (Sell-Side Liquidity Hunt at {last_low}) - Bullish Trap Alert"

        return "No Active Liquidity Hunt (Order Flow Normal)"

    @classmethod
    def calculate_premium_discount(cls, df):
        """Calculates Fibonacci 50% Equilibrium and 61.8-78.6% OTE Zones."""
        high = df['High'].max()
        low = df['Low'].min()
        spot = df['Close'].iloc[-1]

        rng = high - low
        if rng <= 0:
            return {'zone': 'Equilibrium', 'fib_50': spot, 'ote_top': spot, 'ote_bottom': spot}

        fib_50 = low + (0.50 * rng)
        ote_bottom = low + (0.618 * rng)
        ote_top = low + (0.786 * rng)

        if spot < fib_50:
            zone = 'Discount Zone (Smart Money Buying Area)'
        elif spot > fib_50:
            zone = 'Premium Zone (Smart Money Selling Area)'
        else:
            zone = 'Equilibrium Zone (50% Fair Value)'

        return {
            'zone': zone,
            'fib_50': round(float(fib_50), 2),
            'ote_bottom': round(float(ote_bottom), 2),
            'ote_top': round(float(ote_top), 2),
            'range_high': round(float(high), 2),
            'range_low': round(float(low), 2)
        }

    @classmethod
    def analyze(cls, df):
        """Runs full Smart Money Concepts analysis & generates SMC Score (-100 to +100)."""
        swing_h, swing_l = cls.identify_swings(df)
        structure = cls.detect_market_structure(df, swing_h, swing_l)
        bull_obs, bear_obs = cls.detect_order_blocks(df)
        fvgs = cls.detect_fair_value_gaps(df)
        liq_sweep = cls.detect_liquidity_sweeps(df, swing_h, swing_l)
        pd_zones = cls.calculate_premium_discount(df)

        score = 0
        reasons = []

        # 1. Market Structure (35 pts)
        if 'Bullish BOS' in structure['structure']:
            score += 35
            reasons.append("Bullish BOS (Break of Structure continuation) (+35)")
        elif 'Bullish CHoCH' in structure['structure']:
            score += 35
            reasons.append("Bullish CHoCH (Change of Character early reversal) (+35)")
        elif 'Bearish BOS' in structure['structure']:
            score -= 35
            reasons.append("Bearish BOS (Break of Structure downward expansion) (-35)")
        elif 'Bearish CHoCH' in structure['structure']:
            score -= 35
            reasons.append("Bearish CHoCH (Change of Character downward reversal) (-35)")

        # 2. Liquidity Sweep (30 pts)
        if 'SSL Sweep' in liq_sweep:
            score += 30
            reasons.append("Sell-Side Liquidity Swept (Smart Money accumulation) (+30)")
        elif 'BSL Sweep' in liq_sweep:
            score -= 30
            reasons.append("Buy-Side Liquidity Swept (Smart Money distribution) (-30)")

        # 3. Premium / Discount Zone (20 pts)
        if 'Discount' in pd_zones['zone']:
            score += 20
            reasons.append("Price in Discount Zone (Favorable Smart Money Longs) (+20)")
        elif 'Premium' in pd_zones['zone']:
            score -= 20
            reasons.append("Price in Premium Zone (Favorable Smart Money Shorts) (-20)")

        # 4. Fresh Order Block Proximity (15 pts)
        spot = df['Close'].iloc[-1]
        for ob in bull_obs:
            if not ob['mitigated'] and 0 <= ob['distance_pct'] <= 0.6:
                score += 15
                reasons.append(f"Near Fresh Bullish Order Block [{ob['bottom']} - {ob['top']}] (+15)")
                break
        for ob in bear_obs:
            if not ob['mitigated'] and 0 <= ob['distance_pct'] <= 0.6:
                score -= 15
                reasons.append(f"Near Fresh Bearish Order Block [{ob['bottom']} - {ob['top']}] (-15)")
                break

        return {
            'smc_score': score,  # -100 to +100
            'structure': structure,
            'bullish_order_blocks': bull_obs,
            'bearish_order_blocks': bear_obs,
            'fair_value_gaps': fvgs,
            'liquidity_sweep': liq_sweep,
            'premium_discount': pd_zones,
            'reasons': reasons
        }
