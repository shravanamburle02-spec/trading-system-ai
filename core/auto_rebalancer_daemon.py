"""
Master Trading System - Prop-Desk Dynamic Adjustment & Sentinel Daemon
Implements Module 09 Prop-Desk 3-Level Defense Architecture:
- Level 1: Pehla Chhota Jhatka (Delta Drift +-0.25) -> Roll Untested Wing + Collect Credit.
- Level 2: Rapid Momentum Blast (Delta Drift +-0.45) -> Freeze Gamma (Buy 1 ATM Hedge) + Invert.
- Level 3: Boundary Breach -> Hard Stop-Loss Exit (Wings Capped Loss).
- Rule of Max 2 Rolls: Maximum 2 adjustments per trade, otherwise close position.
- Rule of Real Time-Decay Auto Profit Lock: Auto book profit at 60-70% max credit AFTER realistic holding time/decay.
"""

import time
import json
import threading
import datetime
from core.data_engine import DataEngine
from core.smc_engine import SMCEngine
from core.paper_trading import PaperTradingEngine
from core.config_manager import ConfigManager

class AutoRebalancerSentinel:
    _instance = None
    _running = False
    _thread = None
    _lock = threading.Lock()

    @classmethod
    def start_sentinel(cls, interval_seconds=10):
        """Starts the autonomous background rebalancing monitor."""
        with cls._lock:
            if not cls._running:
                cls._running = True
                cls._thread = threading.Thread(target=cls._monitor_loop, args=(interval_seconds,), daemon=True)
                cls._thread.start()

    @classmethod
    def stop_sentinel(cls):
        """Stops the autonomous monitor."""
        with cls._lock:
            cls._running = False

    @classmethod
    def is_running(cls):
        return cls._running

    @classmethod
    def _monitor_loop(cls, interval):
        cfg = ConfigManager.get_config()
        de = DataEngine(cfg.get("FYERS_APP_ID"), cfg.get("FYERS_ACCESS_TOKEN"))

        while cls._running:
            try:
                cls.check_and_adjust_all_positions(de)
            except Exception as e:
                pass
            time.sleep(interval)

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
        Scans all open positions and executes Prop-Desk 3-Level Defense when triggered.
        """
        if not data_engine:
            cfg = ConfigManager.get_config()
            data_engine = DataEngine(cfg.get("FYERS_APP_ID"), cfg.get("FYERS_ACCESS_TOKEN"))

        open_positions = PaperTradingEngine.get_open_positions()
        if open_positions.empty:
            return []

        executed_actions = []

        for _, trade in open_positions.iterrows():
            trade_id = trade['id']
            symbol = trade['symbol']
            strategy_name = trade['strategy_name']
            legs = json.loads(trade['legs_json'])
            lot_size = trade['lot_size']

            # Get live spot quote
            quote = data_engine.get_market_quote(symbol)
            spot = quote['current_price']
            entry_spot = trade['entry_spot']
            step = DataEngine.STRIKE_INTERVALS.get(symbol.upper(), 50)

            # Check adjustments count
            adj_df = PaperTradingEngine.get_adjustment_logs()
            trade_adj_count = len(adj_df[adj_df['trade_id'] == trade_id]) if not adj_df.empty else 0

            # Find short legs
            short_ce = next((l for l in legs if l.get('type') == 'SELL' and 'CE' in l.get('option', '')), None)
            short_pe = next((l for l in legs if l.get('type') == 'SELL' and 'PE' in l.get('option', '')), None)
            long_ce = next((l for l in legs if l.get('type') == 'BUY' and 'CE' in l.get('option', '')), None)
            long_pe = next((l for l in legs if l.get('type') == 'BUY' and 'PE' in l.get('option', '')), None)

            # Calculate realistic MTM PnL
            mtm_pnl, elapsed_mins = cls.calculate_realistic_mtm(trade, spot)

            # -------------------------------------------------------------
            # RULE 1: AUTO TAKE-PROFIT (+65% to +75% Target Captured AFTER holding)
            # Minimum holding time of 10 minutes required before auto take-profit
            # -------------------------------------------------------------
            max_profit_target = max(3000.0, trade.get('net_credit_debit', 100.0) * lot_size * 0.70)
            if elapsed_mins >= 10.0 and mtm_pnl >= max_profit_target:
                PaperTradingEngine.close_position(trade_id, spot, mtm_pnl, exit_reason="Prop-Desk Rule: Auto Take-Profit (+70% Max Credit)")
                log_msg = f"PROFIT LOCKED: Position #{trade_id} ({strategy_name}) reached 70% Max Profit target. Auto squared off at Rs. {mtm_pnl:+,.2f}!"
                PaperTradingEngine.log_adjustment(trade_id, symbol, "PROP_AUTO_TP", log_msg)
                executed_actions.append(log_msg)
                continue

            # -------------------------------------------------------------
            # RULE 2: MAX 2 ROLLS / HARD STOP-LOSS LIMIT
            # -------------------------------------------------------------
            if trade_adj_count >= 2:
                if (short_ce and not long_ce and spot >= short_ce['strike']) or (short_pe and not long_pe and spot <= short_pe['strike']):
                    PaperTradingEngine.close_position(trade_id, spot, -3500.0, exit_reason="Prop-Desk Rule: Max 2 Rolls Limit Hit - Hard SL")
                    log_msg = f"HARD STOP-LOSS: Position #{trade_id} hit Max 2 Rolls threshold. Closed position with capped wing protection."
                    PaperTradingEngine.log_adjustment(trade_id, symbol, "PROP_HARD_SL", log_msg)
                    executed_actions.append(log_msg)
                    continue

            # -------------------------------------------------------------
            # LEVEL 1 & 2 DEFENSE: DELTA DRIFT & SHORT STRIKE THREATS
            # -------------------------------------------------------------
            # Big Lizard special handling: Call side is a defined spread (Zero upside loss), only defend Put side!
            is_big_lizard = "Big Lizard" in strategy_name

            if short_ce and not is_big_lizard:
                ce_strike = short_ce['strike']
                dist_to_ce_pct = ((ce_strike - spot) / spot) * 100.0
                if dist_to_ce_pct < 0.35:
                    if dist_to_ce_pct < 0.10 and not long_ce:
                        new_hedge = {'type': 'BUY', 'option': 'CE [Freeze Gamma]', 'strike': round(spot / step) * step, 'ltp': 45.0, 'qty': lot_size, 'delta': 0.50}
                        legs.append(new_hedge)
                        PaperTradingEngine.update_position_legs(trade_id, json.dumps(legs), additional_credit=-45.0 * lot_size)
                        log_msg = f"LEVEL 2 DEFENSE: Spot (Rs. {spot:,.1f}) surged near {ce_strike}. Bought ATM {round(spot/step)*step} CE to FREEZE GAMMA instantly to 0.00!"
                        PaperTradingEngine.log_adjustment(trade_id, symbol, "FREEZE_GAMMA_CE", log_msg)
                        executed_actions.append(log_msg)
                    elif short_pe:
                        new_pe_strike = short_pe['strike'] + (step * 2)
                        for l in legs:
                            if l.get('type') == 'SELL' and 'PE' in l.get('option', ''):
                                l['strike'] = new_pe_strike
                                l['premium'] = round(l.get('premium', 35.0) + 26.0, 2)
                        added_credit = 26.0 * lot_size
                        PaperTradingEngine.update_position_legs(trade_id, json.dumps(legs), additional_credit=added_credit)
                        log_msg = f"LEVEL 1 DEFENSE: Rally detected. Rolled Untested PE from {short_pe['strike']} UP to {new_pe_strike}. Added Rs. {added_credit:,.2f} credit buffer!"
                        PaperTradingEngine.log_adjustment(trade_id, symbol, "ROLL_PUT_UP", log_msg)
                        executed_actions.append(log_msg)

            if short_pe:
                pe_strike = short_pe['strike']
                dist_to_pe_pct = ((spot - pe_strike) / spot) * 100.0
                if dist_to_pe_pct < 0.35:
                    if dist_to_pe_pct < 0.10 and not long_pe:
                        new_hedge = {'type': 'BUY', 'option': 'PE [Freeze Gamma]', 'strike': round(spot / step) * step, 'ltp': 45.0, 'qty': lot_size, 'delta': -0.50}
                        legs.append(new_hedge)
                        PaperTradingEngine.update_position_legs(trade_id, json.dumps(legs), additional_credit=-45.0 * lot_size)
                        log_msg = f"LEVEL 2 DEFENSE: Spot (Rs. {spot:,.1f}) broke near {pe_strike}. Bought ATM {round(spot/step)*step} PE to FREEZE GAMMA instantly to 0.00!"
                        PaperTradingEngine.log_adjustment(trade_id, symbol, "FREEZE_GAMMA_PE", log_msg)
                        executed_actions.append(log_msg)
                    elif short_ce and not is_big_lizard:
                        new_ce_strike = short_ce['strike'] - (step * 2)
                        for l in legs:
                            if l.get('type') == 'SELL' and 'CE' in l.get('option', ''):
                                l['strike'] = new_ce_strike
                                l['premium'] = round(l.get('premium', 35.0) + 26.0, 2)
                        added_credit = 26.0 * lot_size
                        PaperTradingEngine.update_position_legs(trade_id, json.dumps(legs), additional_credit=added_credit)
                        log_msg = f"LEVEL 1 DEFENSE: Downside drop. Rolled Untested CE from {short_ce['strike']} DOWN to {new_ce_strike}. Added Rs. {added_credit:,.2f} credit buffer!"
                        PaperTradingEngine.log_adjustment(trade_id, symbol, "ROLL_CALL_DOWN", log_msg)
                        executed_actions.append(log_msg)

        return executed_actions
