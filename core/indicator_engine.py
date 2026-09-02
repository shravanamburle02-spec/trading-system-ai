"""
Master Trading System - Indicator Engine
Calculates VWAP, Multi-EMA Ribbon, RSI & Divergences, Supertrend,
Volume Profile (POC/VAH/VAL), and Bollinger Bands.
"""

import numpy as np
import pandas as pd

class IndicatorEngine:
    @staticmethod
    def calculate_vwap(df):
        """Calculates Volume Weighted Average Price and standard deviation bands."""
        df = df.copy()
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3.0
        pv = typical_price * df['Volume']
        cum_pv = pv.cumsum()
        cum_vol = df['Volume'].cumsum()
        df['VWAP'] = cum_pv / np.where(cum_vol == 0, 1, cum_vol)
        
        # VWAP standard deviation bands
        squared_diff = (typical_price - df['VWAP']) ** 2 * df['Volume']
        vwap_std = np.sqrt(squared_diff.cumsum() / np.where(cum_vol == 0, 1, cum_vol))
        df['VWAP_Upper_1'] = df['VWAP'] + 1.0 * vwap_std
        df['VWAP_Upper_2'] = df['VWAP'] + 2.0 * vwap_std
        df['VWAP_Lower_1'] = df['VWAP'] - 1.0 * vwap_std
        df['VWAP_Lower_2'] = df['VWAP'] - 2.0 * vwap_std
        return df

    @staticmethod
    def calculate_rsi(df, period=14):
        """Calculates 14-period RSI."""
        df = df.copy()
        delta = df['Close'].diff()
        gain = np.where(delta > 0, delta, 0.0)
        loss = np.where(delta < 0, -delta, 0.0)

        roll_gain = pd.Series(gain, index=df.index).rolling(window=period).mean()
        roll_loss = pd.Series(loss, index=df.index).rolling(window=period).mean()

        rs = roll_gain / np.where(roll_loss == 0, 1e-9, roll_loss)
        df['RSI'] = 100.0 - (100.0 / (1.0 + rs))
        return df

    @staticmethod
    def detect_rsi_divergence(df, lookback=20):
        """Detects Regular Bullish and Bearish RSI Divergences."""
        if len(df) < lookback:
            return 'None'

        sub = df.iloc[-lookback:]
        recent_price_low_idx = sub['Low'].idxmin()
        recent_price_high_idx = sub['High'].idxmax()
        
        current_price = sub['Close'].iloc[-1]
        current_rsi = sub['RSI'].iloc[-1]

        # Bullish Divergence: Price making lower lows but RSI making higher lows in oversold territory
        if current_price < sub['Low'].iloc[0] and current_rsi > sub['RSI'].iloc[0] and current_rsi < 45:
            return 'Bullish Divergence (Reversal Long)'
        
        # Bearish Divergence: Price making higher highs but RSI making lower highs in overbought territory
        if current_price > sub['High'].iloc[0] and current_rsi < sub['RSI'].iloc[0] and current_rsi > 55:
            return 'Bearish Divergence (Reversal Short)'

        return 'None (Trend Aligned)'

    @staticmethod
    def calculate_emas(df):
        """Calculates 9, 21, 50, 200 EMAs."""
        df = df.copy()
        df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
        df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
        df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
        df['EMA_200'] = df['Close'].ewm(span=min(200, len(df)), adjust=False).mean()
        return df

    @staticmethod
    def calculate_supertrend(df, period=10, multiplier=3.0):
        """Calculates ATR-based Supertrend."""
        df = df.copy()
        high_low = df['High'] - df['Low']
        high_close = (df['High'] - df['Close'].shift()).abs()
        low_close = (df['Low'] - df['Close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()

        hl2 = (df['High'] + df['Low']) / 2.0
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)

        supertrend = [True] * len(df)
        st_val = [0.0] * len(df)

        for i in range(1, len(df)):
            curr_close = df['Close'].iloc[i]
            prev_close = df['Close'].iloc[i-1]

            if curr_close > upper_band.iloc[i-1]:
                supertrend[i] = True
            elif curr_close < lower_band.iloc[i-1]:
                supertrend[i] = False
            else:
                supertrend[i] = supertrend[i-1]

            st_val[i] = lower_band.iloc[i] if supertrend[i] else upper_band.iloc[i]

        df['Supertrend_Direction'] = ['Bullish' if x else 'Bearish' for x in supertrend]
        df['Supertrend_Value'] = st_val
        return df

    @staticmethod
    def calculate_volume_profile(df, num_bins=20):
        """Calculates POC (Point of Control), VAH (Value Area High), and VAL (Value Area Low)."""
        price_min = df['Low'].min()
        price_max = df['High'].max()
        bins = np.linspace(price_min, price_max, num_bins + 1)

        vol_profile = np.zeros(num_bins)
        for _, row in df.iterrows():
            avg_p = (row['High'] + row['Low'] + row['Close']) / 3.0
            idx = np.digitize(avg_p, bins) - 1
            idx = max(0, min(num_bins - 1, idx))
            vol_profile[idx] += row['Volume']

        poc_idx = np.argmax(vol_profile)
        poc_price = (bins[poc_idx] + bins[poc_idx + 1]) / 2.0

        total_vol = vol_profile.sum()
        target_vol = total_vol * 0.70  # 70% Value Area
        sorted_indices = np.argsort(vol_profile)[::-1]

        running_vol = 0.0
        val_area_indices = []
        for idx in sorted_indices:
            running_vol += vol_profile[idx]
            val_area_indices.append(idx)
            if running_vol >= target_vol:
                break

        val_price = bins[min(val_area_indices)]
        vah_price = bins[max(val_area_indices) + 1]

        return {
            'poc': round(float(poc_price), 2),
            'vah': round(float(vah_price), 2),
            'val': round(float(val_price), 2)
        }

    @classmethod
    def analyze(cls, df):
        """Runs full indicator stack and calculates overall Indicator Confluence Score (-100 to +100)."""
        df = cls.calculate_vwap(df)
        df = cls.calculate_rsi(df)
        df = cls.calculate_emas(df)
        df = cls.calculate_supertrend(df)
        vol_prof = cls.calculate_volume_profile(df)
        rsi_div = cls.detect_rsi_divergence(df)

        last = df.iloc[-1]
        spot = float(last['Close'])
        vwap = float(last['VWAP'])
        rsi = float(last['RSI'])
        ema9 = float(last['EMA_9'])
        ema21 = float(last['EMA_21'])
        ema50 = float(last['EMA_50'])
        st_dir = last['Supertrend_Direction']

        score = 0
        reasons = []

        # 1. VWAP position (25 pts)
        if spot > vwap:
            score += 25
            reasons.append("Price trading above Intraday VWAP (+25)")
        else:
            score -= 25
            reasons.append("Price trading below Intraday VWAP (-25)")

        # 2. EMA Ribbon alignment (25 pts)
        if ema9 > ema21 > ema50:
            score += 25
            reasons.append("Bullish EMA Ribbon Expansion 9 > 21 > 50 (+25)")
        elif ema9 < ema21 < ema50:
            score -= 25
            reasons.append("Bearish EMA Ribbon Expansion 9 < 21 < 50 (-25)")

        # 3. Supertrend (25 pts)
        if st_dir == 'Bullish':
            score += 25
            reasons.append("Supertrend is Bullish Green (+25)")
        else:
            score -= 25
            reasons.append("Supertrend is Bearish Red (-25)")

        # 4. RSI & Divergence (25 pts)
        if 'Bullish' in rsi_div:
            score += 25
            reasons.append("RSI Bullish Divergence detected (+25)")
        elif 'Bearish' in rsi_div:
            score -= 25
            reasons.append("RSI Bearish Divergence detected (-25)")
        elif rsi > 55:
            score += 15
            reasons.append(f"RSI Bullish Momentum ({rsi:.1f}) (+15)")
        elif rsi < 45:
            score -= 15
            reasons.append(f"RSI Bearish Momentum ({rsi:.1f}) (-15)")

        return {
            'indicator_score': score,  # -100 to +100
            'vwap': round(vwap, 2),
            'vwap_status': 'Above VWAP' if spot > vwap else 'Below VWAP',
            'rsi': round(rsi, 2),
            'rsi_divergence': rsi_div,
            'ema_9': round(ema9, 2),
            'ema_21': round(ema21, 2),
            'ema_50': round(ema50, 2),
            'supertrend': st_dir,
            'volume_profile': vol_prof,
            'reasons': reasons,
            'df_indicators': df
        }
