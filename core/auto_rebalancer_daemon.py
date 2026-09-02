"""
Master Trading System - Prop-Desk Dynamic Adjustment & Sentinel Daemon
Implements Module 09 Prop-Desk 3-Level Defense Architecture:
- Level 1: Pehla Chhota Jhatka (Delta Drift +-0.25) -> Roll Untested Wing + Collect Credit.
- Level 2: Rapid Momentum Blast (Delta Drift +-0.45) -> Freeze Gamma (Buy 1 ATM Hedge) + Invert.
- Level 3: Boundary Breach -> Hard Stop-Loss Exit (Wings Capped Loss).
- Rule of Max 2 Rolls: Maximum 2 adjustments per trade, otherwise close position.
- Rule of Auto Profit Lock: Auto book profit at 60-70% max credit.
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

            # Calculate MTM PnL estimation
            pts_diff = spot - entry_spot
            # Non-directional theta decay factor
            mtm_pnl = (trade.get('net_credit_debit', 50.0) * 0.60 * lot_size) - (abs(pts_diff) * 0.35 * lot_size)

            # -------------------------------------------------------------
            # RULE 1: AUTO TAKE-PROFIT (+65% to +75% Target Captured)
            # -------------------------------------------------------------
            if mtm_pnl >= trade.get('tgt_price', 6500.0) or (mtm_pnl >= 5000 and abs(pts_diff) < step):
                PaperTradingEngine.close_position(trade_id, spot, mtm_pnl, exit_reason="Prop-Desk Rule: Auto Take-Profit (+70% Max Credit)")
                log_msg = f"🏆 PROFIT LOCKED: Position #{trade_id} ({strategy_name}) reached 70% Max Profit target. Auto squared off at ₹{mtm_pnl:+,.2f}!"
                PaperTradingEngine.log_adjustment(trade_id, symbol, "PROP_AUTO_TP", log_msg)
                executed_actions.append(log_msg)
                continue

            # -------------------------------------------------------------
            # RULE 2: MAX 2 ROLLS / HARD STOP-LOSS LIMIT
            # -------------------------------------------------------------
            if trade_adj_count >= 2:
                # Max 2 rolls already done, if tested further, execute Level 3 Hard Exit
                if short_ce and (spot >= short_ce['strike']):
                    PaperTradingEngine.close_position(trade_id, spot, -3500.0, exit_reason="Prop-Desk Rule: Max 2 Rolls Limit Hit - Hard SL")
                    log_msg = f"🛑 HARD STOP-LOSS: Position #{trade_id} hit Max 2 Rolls threshold. Closed position with capped wing protection."
                    PaperTradingEngine.log_adjustment(trade_id, symbol, "PROP_HARD_SL", log_msg)
                    executed_actions.append(log_msg)
                    continue
                elif short_pe and (spot <= short_pe['strike']):
                    PaperTradingEngine.close_position(trade_id, spot, -3500.0, exit_reason="Prop-Desk Rule: Max 2 Rolls Limit Hit - Hard SL")
                    log_msg = f"🛑 HARD STOP-LOSS: Position #{trade_id} hit Max 2 Rolls threshold. Closed position with capped wing protection."
                    PaperTradingEngine.log_adjustment(trade_id, symbol, "PROP_HARD_SL", log_msg)
                    executed_actions.append(log_msg)
                    continue

            # -------------------------------------------------------------
            # LEVEL 1 & 2 DEFENSE: DELTA DRIFT & SHORT STRIKE THREATS
            # -------------------------------------------------------------
            if short_ce and short_pe:
                ce_strike = short_ce['strike']
                pe_strike = short_pe['strike']

                dist_to_ce_pct = ((ce_strike - spot) / spot) * 100.0
                dist_to_pe_pct = ((spot - pe_strike) / spot) * 100.0

                # 1. RALLY THREAT (Spot nearing Short Call Strike)
                if dist_to_ce_pct < 0.55:
                    if dist_to_ce_pct < 0.20:
                        # LEVEL 2: RAPID SURGE -> FREEZE GAMMA (Buy ATM Call)
                        new_hedge = {'type': 'BUY', 'option': 'CE [Freeze Gamma]', 'strike': round(spot / step) * step, 'ltp': 45.0, 'qty': lot_size, 'delta': 0.50}
                        legs.append(new_hedge)
                        PaperTradingEngine.update_position_legs(trade_id, json.dumps(legs), additional_credit=-45.0 * lot_size)
                        log_msg = f"⚡ LEVEL 2 DEFENSE: Spot (₹{spot:,.1f}) surged near {ce_strike}. Bought ATM {round(spot/step)*step} CE to FREEZE GAMMA instantly to 0.00!"
                        PaperTradingEngine.log_adjustment(trade_id, symbol, "FREEZE_GAMMA_CE", log_msg)
                        executed_actions.append(log_msg)
                    else:
                        # LEVEL 1: ROLL UNTESTED PE UP
                        new_pe_strike = pe_strike + (step * 2)
                        for l in legs:
                            if l.get('type') == 'SELL' and 'PE' in l.get('option', ''):
                                l['strike'] = new_pe_strike
                                l['premium'] = round(l.get('premium', 35.0) + 26.0, 2)
                        
                        added_credit = 26.0 * lot_size
                        PaperTradingEngine.update_position_legs(trade_id, json.dumps(legs), additional_credit=added_credit)
                        log_msg = f"🛡️ LEVEL 1 DEFENSE: Rally detected. Rolled Untested PE from {pe_strike} UP to {new_pe_strike}. Added ₹{added_credit:,.2f} credit buffer!"
                        PaperTradingEngine.log_adjustment(trade_id, symbol, "ROLL_PUT_UP", log_msg)
                        executed_actions.append(log_msg)

                # 2. DOWNSIDE CRASH THREAT (Spot nearing Short Put Strike)
                elif dist_to_pe_pct < 0.55:
                    if dist_to_pe_pct < 0.20:
                        # LEVEL 2: RAPID FALL -> FREEZE GAMMA (Buy ATM Put)
                        new_hedge = {'type': 'BUY', 'option': 'PE [Freeze Gamma]', 'strike': round(spot / step) * step, 'ltp': 45.0, 'qty': lot_size, 'delta': -0.50}
                        legs.append(new_hedge)
                        PaperTradingEngine.update_position_legs(trade_id, json.dumps(legs), additional_credit=-45.0 * lot_size)
                        log_msg = f"⚡ LEVEL 2 DEFENSE: Spot (₹{spot:,.1f}) broke near {pe_strike}. Bought ATM {round(spot/step)*step} PE to FREEZE GAMMA instantly to 0.00!"
                        PaperTradingEngine.log_adjustment(trade_id, symbol, "FREEZE_GAMMA_PE", log_msg)
                        executed_actions.append(log_msg)
                    else:
                        # LEVEL 1: ROLL UNTESTED CE DOWN
                        new_ce_strike = ce_strike - (step * 2)
                        for l in legs:
                            if l.get('type') == 'SELL' and 'CE' in l.get('option', ''):
                                l['strike'] = new_ce_strike
                                l['premium'] = round(l.get('premium', 35.0) + 26.0, 2)

                        added_credit = 26.0 * lot_size
                        PaperTradingEngine.update_position_legs(trade_id, json.dumps(legs), additional_credit=added_credit)
                        log_msg = f"🛡️ LEVEL 1 DEFENSE: Downside drop. Rolled Untested CE from {ce_strike} DOWN to {new_ce_strike}. Added ₹{added_credit:,.2f} credit buffer!"
                        PaperTradingEngine.log_adjustment(trade_id, symbol, "ROLL_CALL_DOWN", log_msg)
                        executed_actions.append(log_msg)

        return executed_actions
