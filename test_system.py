"""
Verification Script to test all engines in Master Trading System.
"""
import sys

print("Testing Data Engine...")
from core.data_engine import DataEngine, BlackScholes
de = DataEngine()
q = de.get_market_quote("NIFTY")
print(f"NIFTY Spot: {q['current_price']}")
chain = de.get_option_chain("NIFTY")
print(f"Option Chain: Max Pain={chain['max_pain']}, PCR={chain['pcr']}, ATM IV={chain['atm_iv']}")

print("\nTesting Indicator Engine...")
from core.indicator_engine import IndicatorEngine
ind = IndicatorEngine.analyze(q['df'])
print(f"Indicators: Score={ind['indicator_score']}, VWAP={ind['vwap']}, RSI={ind['rsi']}")

print("\nTesting SMC Engine...")
from core.smc_engine import SMCEngine
smc = SMCEngine.analyze(q['df'])
print(f"SMC: Score={smc['smc_score']}, Structure={smc['structure']['structure']}")

print("\nTesting Confluence Engine...")
from core.confluence_engine import ConfluenceEngine
fii = de.get_fii_dii_sentiment()
conf = ConfluenceEngine.evaluate(chain, ind, smc, fii)
print(f"Confluence: Bias={conf['market_bias']}, Score={conf['composite_score']}, Agreement={conf['confluence_pct']}%")

print("\nTesting Strategy Optimizer...")
from core.strategy_optimizer import StrategyOptimizer
dir_strat = StrategyOptimizer.generate_directional_strategy("NIFTY", q['current_price'], conf['market_bias'], conf['confluence_pct'], chain['chain_df'], smc)
print(f"Directional Strategy: {dir_strat['strategy_name']} (Win Prob: {dir_strat['win_probability']})")
non_dir = StrategyOptimizer.generate_custom_non_directional("NIFTY", q['current_price'], chain)
print(f"Non-Directional: {non_dir['strategy_name']} (Win Prob: {non_dir['win_probability']})")

print("\nTesting Risk & Paper Trading Engine...")
from core.paper_trading import PaperTradingEngine
from core.risk_shield import RiskShield
paper = PaperTradingEngine()
paper.init_db()
acc = paper.get_account()
print(f"Virtual Balance: Rs. {acc['balance']}")
tid = paper.execute_paper_trade("NIFTY", dir_strat, q['current_price'], conf['confluence_pct'])
print(f"Paper Trade Executed: ID #{tid}")
paper.close_position(tid, q['current_price'] + 25, 625.0, "Target 1 Hit")
print("Position Closed & Logged to Journal.")

print("\nALL ENGINES PASSED 100% SUCCESSFULLY!")
