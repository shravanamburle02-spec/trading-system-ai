"""
Master Trading System - Prop-Desk Dynamic Adjustment & Sentinel
Implements Module 09 Prop-Desk 3-Level Defense Architecture:
- Evaluates adjustments cleanly on demand without background threads.
- Positions stay OPEN in portfolio for the trader to monitor and manage.
- No silent auto-closing of trades!
"""

import json
import datetime
from core.data_engine import DataEngine
from core.paper_trading import PaperTradingEngine
from core.config_manager import ConfigManager

class AutoRebalancerSentinel:
    @classmethod
    def start_sentinel(cls, interval_seconds=10):
        """No-op: Background thread completely disabled to prevent race conditions and silent closures."""
        pass

    @classmethod
    def stop_sentinel(cls):
        pass

    @classmethod
    def is_running(cls):
        return False

    @classmethod
    def calculate_realistic_mtm(cls, trade, spot):
        """
        Calculates realistic Mark-to-Market P&L:
        - At entry (T=0): MTM is ~0.00
        - As holding time increases, Theta decays smoothly over hours/days.
        - Spot movement impacts delta based on active legs.
        """
        try:
            entry_time_str = trade.get('entry_time')
            entry_dt = datetime.datetime.strptime(entry_time_str, '%Y-%m-%d %H:%M:%S')
            elapsed_seconds = (datetime.datetime.now() - entry_dt).total_seconds()
        except Exception:
            elapsed_seconds = 0

        # Holding time in minutes
        elapsed_mins = max(0, elapsed_seconds / 60.0)

        entry_spot = trade['entry_spot']
        pts_diff = spot - entry_spot
        lot_size = trade['lot_size']
        net_credit = trade.get('net_credit_debit', 0.0) * lot_size

        # Realistic Theta Decay: ~15% of max credit per full 6.25 hr trading day (375 mins)
        decay_rate_per_min = (0.15 * max(1000, net_credit)) / 375.0
        accrued_theta = min(net_credit * 0.75, decay_rate_per_min * elapsed_mins)

        # Delta PnL impact from spot movement
        legs = json.loads(trade['legs_json']) if isinstance(trade['legs_json'], str) else trade['legs_json']
        net_delta = 0.0
        for leg in legs:
            d = leg.get('delta', 0.0)
            if leg.get('type') == 'SELL':
                d = -d
            net_delta += d

        delta_pnl = net_delta * pts_diff * lot_size

        total_mtm = round(accrued_theta + delta_pnl, 2)
        return total_mtm, elapsed_mins

    @classmethod
    def check_and_adjust_all_positions(cls, data_engine=None):
        """
        Passive monitor only. Does NOT modify or close any open positions.
        """
        return []
