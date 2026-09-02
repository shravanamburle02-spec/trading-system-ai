"""
Master Trading System - Risk Management & High-Impact Event Shield
Calculates Dynamic Position Sizing based on Capital & VIX, enforces Daily Max Loss limits,
and monitors high-volatility macroeconomic events.
"""

import datetime

class RiskShield:
    HIGH_IMPACT_EVENTS = [
        {'event': 'RBI Monetary Policy Committee (MPC) Rate Decision', 'risk_level': 'HIGH', 'impact': 'Extreme Banking Sector & VIX Spikes'},
        {'event': 'US Federal Reserve FOMC Interest Rate Decision', 'risk_level': 'HIGH', 'impact': 'Global Market Direction & Gap Openings'},
        {'event': 'India Union Budget Presentation', 'risk_level': 'CRITICAL', 'impact': 'Massive IV Surge & Trend Reversals'},
        {'event': 'US CPI Inflation Data Release', 'risk_level': 'MEDIUM', 'impact': 'Tech & Global Equities Volatility'},
        {'event': 'India CPI & Industrial Production (IIP)', 'risk_level': 'MEDIUM', 'impact': 'Macro Sentiment Shift'}
    ]

    @staticmethod
    def calculate_lot_size(account_capital, risk_per_trade_pct=1.5, per_lot_risk=1500, vix=14.0):
        """
        Calculates optimal lot size based on account balance, risk tolerance, and current VIX.
        VIX scaling: If VIX > 18, position size is reduced to dampen volatility exposure.
        """
        total_risk_allowed = account_capital * (risk_per_trade_pct / 100.0)
        
        # Volatility multiplier
        if vix > 22.0:
            vol_multiplier = 0.50 # Cut size by half in extreme volatility
        elif vix > 17.0:
            vol_multiplier = 0.75 # Cut size by 25% in high volatility
        else:
            vol_multiplier = 1.00 # Standard sizing

        raw_lots = (total_risk_allowed / max(100.0, per_lot_risk)) * vol_multiplier
        recommended_lots = max(1, int(raw_lots))

        return {
            'account_capital': account_capital,
            'risk_per_trade_inr': round(total_risk_allowed, 2),
            'recommended_lots': recommended_lots,
            'vix_adjustment_factor': f"{int(vol_multiplier * 100)}%",
            'max_capital_allocation': round(account_capital * 0.35, 2) # Max 35% margin utilized per trade
        }

    @staticmethod
    def check_daily_drawdown(account_capital, daily_pnl, max_daily_loss_pct=3.0):
        """Checks if daily loss threshold has been breached to lock trading and prevent revenge trades."""
        max_allowed_loss = account_capital * (max_daily_loss_pct / 100.0)
        is_breached = daily_pnl <= -max_allowed_loss

        return {
            'daily_pnl': round(daily_pnl, 2),
            'max_allowed_daily_loss': round(-max_allowed_loss, 2),
            'is_breached': is_breached,
            'status': "🚨 TRADE LOCKDOWN ACTIVE: Daily Max Loss Hit! Please stop trading for the day to preserve emotional capital." if is_breached else "🟢 Risk Limits Healthy"
        }

    @classmethod
    def get_event_shield_status(cls):
        """Returns current High-Impact macroeconomic event alerts."""
        today = datetime.date.today().strftime('%Y-%m-%d')
        # Return mock real-time calendar status
        return {
            'event_status': '🟡 CAUTION: US FOMC & India CPI Week',
            'warning': "High-impact macro event window active. Strictly avoid naked overnight selling. Keep defined-risk spreads with hedged wings.",
            'tracked_events': cls.HIGH_IMPACT_EVENTS
        }
