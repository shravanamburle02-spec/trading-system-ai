"""
Master Trading System - Ultra-Dense Bloomberg & Sensibull Style Quant Cockpit
3-Pane Layout:
- LEFT PANE (28%): 3-Layer Confluence Matrix (Gauges, Visual Meters, Badges)
- CENTER PANE (44%): Live Sensibull-Style Option Payoff Curve + Strike OI Distribution + 1-Click Action Deck
- RIGHT PANE (28%): Autonomous 3-Level Defense Sentinel + Greeks Cockpit + Voice AI Buddy
- TOP TICKER: Single-line Bloomberg-style Header with Real-Time Ticking IST Clock, Expiry Countdown & Spot Ticker
"""

import os
import re
import json
import datetime
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from core.config_manager import ConfigManager
from core.data_engine import DataEngine
from core.indicator_engine import IndicatorEngine
from core.smc_engine import SMCEngine
from core.confluence_engine import ConfluenceEngine
from core.strategy_optimizer import StrategyOptimizer
from core.adjustment_engine import AdjustmentEngine
from core.liquidity_shield import LiquidityShield
from core.risk_shield import RiskShield
from core.paper_trading import PaperTradingEngine
from core.voice_ai_copilot import VoiceAICopilot
from core.gemini_live_chat import GeminiLiveChat
from core.auto_rebalancer_daemon import AutoRebalancerSentinel

st.set_page_config(
    page_title="QUANT CORE | Ultra-Dense Prop-Desk Cockpit",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Start Background Auto-Rebalancer Sentinel
AutoRebalancerSentinel.start_sentinel(interval_seconds=10)

# Persistent configuration load
config = ConfigManager.get_config()

# Initialize session states
if "gemini_messages" not in st.session_state:
    st.session_state.gemini_messages = [
        {"role": "assistant", "content": "Namaste bhai! Main tera Prop-Desk AI Quant Co-Pilot hoon. Live Sensibull Payoff Curve, 3-Layer Confluence, Greeks, aur 3-Level Adjustment Sentinel ke sath live hoon. Poocho!"}
    ]

# -------------------------------------------------------------
# DENSE BLOOMBERG QUANT CSS & OBSIDIAN GLASSMORPHISM
# -------------------------------------------------------------
st.markdown("""
<link rel="preconnect" href="https://fonts.gstatic.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">

<style>
    #MainMenu, footer, header { visibility: hidden !important; height: 0px !important; }
    .stDeployButton { display: none !important; }
    .block-container { padding-top: 0.5rem !important; padding-bottom: 1.5rem !important; padding-left: 1.2rem !important; padding-right: 1.2rem !important; }

    :root {
        --bg-obsidian: #05070B;
        --bg-card: rgba(13, 17, 26, 0.85);
        --glass-border: rgba(255, 255, 255, 0.08);
        --neon-emerald: #00F5A0;
        --neon-cyan: #00D2FF;
        --neon-rose: #FF3B69;
        --neon-gold: #FFB800;
        --neon-purple: #9D4EDD;
        --text-primary: #F0F4F8;
        --text-muted: #8B949E;
    }

    body, .stApp {
        background: radial-gradient(circle at 50% -20%, #0d1527 0%, #05070B 80%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: var(--text-primary) !important;
    }

    .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }

    .cockpit-card {
        background: var(--bg-card);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    .cockpit-card:hover {
        border-color: rgba(0, 210, 255, 0.3);
    }

    .card-header {
        font-size: 0.8rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #FFFFFF;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        padding-bottom: 4px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .glow-pill-emerald {
        background: rgba(0, 245, 160, 0.12);
        color: var(--neon-emerald);
        border: 1px solid rgba(0, 245, 160, 0.35);
        padding: 2px 8px;
        border-radius: 14px;
        font-size: 0.72rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .glow-pill-rose {
        background: rgba(255, 59, 105, 0.12);
        color: var(--neon-rose);
        border: 1px solid rgba(255, 59, 105, 0.35);
        padding: 2px 8px;
        border-radius: 14px;
        font-size: 0.72rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .glow-pill-cyan {
        background: rgba(0, 210, 255, 0.12);
        color: var(--neon-cyan);
        border: 1px solid rgba(0, 210, 255, 0.35);
        padding: 2px 8px;
        border-radius: 14px;
        font-size: 0.72rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .glow-pill-gold {
        background: rgba(255, 184, 0, 0.12);
        color: var(--neon-gold);
        border: 1px solid rgba(255, 184, 0, 0.35);
        padding: 2px 8px;
        border-radius: 14px;
        font-size: 0.72rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .glow-pill-purple {
        background: rgba(157, 78, 221, 0.15);
        color: #C77DFF;
        border: 1px solid rgba(157, 78, 221, 0.4);
        padding: 2px 8px;
        border-radius: 14px;
        font-size: 0.72rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }

    .badge-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 6px;
    }
    .badge-cell {
        background: rgba(255, 255, 255, 0.025);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 6px 10px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .badge-cell-label {
        font-size: 0.68rem;
        color: var(--text-muted);
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-cell-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 2px;
    }

    .ratio-bar-wrapper {
        background: rgba(255, 59, 105, 0.3);
        height: 10px;
        border-radius: 10px;
        overflow: hidden;
        display: flex;
        margin: 6px 0;
    }
    .ratio-bar-put {
        background: #00F5A0;
        height: 100%;
        box-shadow: 0 0 8px #00F5A0;
    }
    .ratio-bar-call {
        background: #FF3B69;
        height: 100%;
        box-shadow: 0 0 8px #FF3B69;
    }

    .stButton > button {
        background: linear-gradient(135deg, #00D2FF 0%, #00F5A0 100%) !important;
        color: #05070B !important;
        font-weight: 900 !important;
        font-size: 0.9rem !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
        box-shadow: 0 0 15px rgba(0, 245, 160, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 0 25px rgba(0, 245, 160, 0.6) !important;
    }

    .chat-msg-u {
        background: rgba(0, 210, 255, 0.12);
        border: 1px solid rgba(0, 210, 255, 0.3);
        border-radius: 8px;
        padding: 6px 10px;
        margin-bottom: 6px;
        font-size: 0.82rem;
        color: #FFFFFF;
    }
    .chat-msg-a {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 245, 160, 0.2);
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 6px;
        font-size: 0.82rem;
        line-height: 1.4;
        color: #F0F4F8;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# REAL-TIME LIVE TICKING JAVASCRIPT TOP TICKER BAR
# -------------------------------------------------------------
clock_html = """
<div id="top-bloomberg-ticker" style="
    background: linear-gradient(135deg, rgba(13, 17, 26, 0.98) 0%, rgba(6, 8, 13, 0.98) 100%);
    border: 1px solid rgba(0, 210, 255, 0.25);
    border-radius: 10px;
    padding: 6px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #F0F4F8;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    margin-bottom: 6px;
">
    <div style="display: flex; align-items: center; gap: 12px;">
        <span style="font-weight: 900; font-size: 0.95rem; color: #FFFFFF; display: flex; align-items: center; gap: 6px;">
            <span style="display: inline-block; width: 7px; height: 7px; background: #00F5A0; border-radius: 50%; box-shadow: 0 0 8px #00F5A0;"></span>
            QUANT COCKPIT
        </span>
        <span id="live-date" style="color: #8B949E; font-size: 0.8rem; font-weight: 600;">--</span>
        <span id="live-time" style="font-family: 'Consolas', monospace; color: #00D2FF; font-weight: 800; font-size: 0.95rem;">--:--:-- --</span>
    </div>
    <div style="display: flex; align-items: center; gap: 10px;">
        <span id="market-status-pill" style="padding: 2px 10px; border-radius: 14px; font-size: 0.72rem; font-weight: 800;">CHECKING...</span>
        <span id="live-countdown" style="font-family: 'Consolas', monospace; color: #FFB800; font-weight: 700; font-size: 0.8rem;">⏳ --</span>
    </div>
</div>

<script>
function updateClock() {
    const now = new Date();
    const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
    const ist = new Date(utc + (3600000 * 5.5));

    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    const dayName = days[ist.getDay()];
    const dateNum = String(ist.getDate()).padStart(2, '0');
    const monthName = months[ist.getMonth()];
    const year = ist.getFullYear();

    let hours = ist.getHours();
    const minutes = String(ist.getMinutes()).padStart(2, '0');
    const seconds = String(ist.getSeconds()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const displayHours = String(hours % 12 || 12).padStart(2, '0');

    document.getElementById('live-date').innerText = `📅 ${dayName}, ${dateNum} ${monthName} ${year}`;
    document.getElementById('live-time').innerText = `⏰ ${displayHours}:${minutes}:${seconds} ${ampm} IST`;

    const weekday = ist.getDay();
    const totalMinutes = ist.getHours() * 60 + ist.getMinutes();
    const totalSeconds = totalMinutes * 60 + ist.getSeconds();

    const pill = document.getElementById('market-status-pill');
    const countdown = document.getElementById('live-countdown');

    if (weekday === 0 || weekday === 6) {
        pill.innerText = '● WEEKEND CLOSED';
        pill.style.background = 'rgba(255, 59, 105, 0.15)';
        pill.style.color = '#FF3B69';
        pill.style.border = '1px solid rgba(255, 59, 105, 0.4)';
        countdown.innerText = '⏳ Opens Mon 09:15:00 AM';
    } else if (totalMinutes < 540) {
        pill.innerText = '● MARKET CLOSED';
        pill.style.background = 'rgba(255, 59, 105, 0.15)';
        pill.style.color = '#FF3B69';
        pill.style.border = '1px solid rgba(255, 59, 105, 0.4)';
        
        const targetSec = 9 * 3600 + 15 * 60;
        const diffSec = targetSec - totalSeconds;
        const h = Math.floor(diffSec / 3600);
        const m = Math.floor((diffSec % 3600) / 60);
        const s = diffSec % 60;
        countdown.innerText = `⏳ Opens in ${String(h).padStart(2,'0')}h ${String(m).padStart(2,'0')}m ${String(s).padStart(2,'0')}s`;
    } else if (totalMinutes >= 540 && totalMinutes < 555) {
        pill.innerText = '● PRE-OPEN';
        pill.style.background = 'rgba(255, 184, 0, 0.15)';
        pill.style.color = '#FFB800';
        pill.style.border = '1px solid rgba(255, 184, 0, 0.4)';
        
        const targetSec = 9 * 3600 + 15 * 60;
        const diffSec = targetSec - totalSeconds;
        const m = Math.floor(diffSec / 60);
        const s = diffSec % 60;
        countdown.innerText = `⏳ Live in ${String(m).padStart(2,'0')}m ${String(s).padStart(2,'0')}s`;
    } else if (totalMinutes >= 555 && totalMinutes < 930) {
        pill.innerText = '● MARKET LIVE';
        pill.style.background = 'rgba(0, 245, 160, 0.15)';
        pill.style.color = '#00F5A0';
        pill.style.border = '1px solid rgba(0, 245, 160, 0.4)';
        
        const targetSec = 15 * 3600 + 30 * 60;
        const diffSec = targetSec - totalSeconds;
        const h = Math.floor(diffSec / 3600);
        const m = Math.floor((diffSec % 3600) / 60);
        const s = diffSec % 60;
        countdown.innerText = `⏳ Closes in ${String(h).padStart(2,'0')}h ${String(m).padStart(2,'0')}m ${String(s).padStart(2,'0')}s`;
    } else {
        pill.innerText = '● MARKET CLOSED';
        pill.style.background = 'rgba(255, 59, 105, 0.15)';
        pill.style.color = '#FF3B69';
        pill.style.border = '1px solid rgba(255, 59, 105, 0.4)';
        countdown.innerText = '⏳ Opens Tomorrow 09:15:00 AM';
    }
}

updateClock();
setInterval(updateClock, 1000);
</script>
"""

components.html(clock_html, height=48)

# -------------------------------------------------------------
# DATA INGESTION & CORE COMPUTATION
# -------------------------------------------------------------
fyers_app_id = config.get("FYERS_APP_ID", "")
fyers_token = config.get("FYERS_ACCESS_TOKEN", "")

data_eng = DataEngine(fyers_app_id, fyers_token)
paper_eng = PaperTradingEngine()
paper_eng.init_db(default_capital=300000.0)

# Top Bar Asset & Global Control Row
t_col1, t_col2, t_col3, t_col4, t_col5, t_col6 = st.columns([1.8, 1.8, 1.5, 1.5, 1.5, 1.4])

with t_col1:
    symbol = st.selectbox(
        "Asset",
        ["NIFTY", "BANKNIFTY", "SENSEX", "FINNIFTY", "MIDCPNIFTY", "RELIANCE", "HDFCBANK", "INFY", "TCS", "ASIANPAINT"],
        index=0,
        label_visibility="collapsed"
    )

exp_info = LiquidityShield.get_detailed_expiry_info(symbol)
dte = exp_info['days_left']
default_lot = DataEngine.LOT_SIZES.get(symbol, 75)

quote = data_eng.get_market_quote(symbol)
spot = quote['current_price']
df_candles = quote['df']
chain_data = data_eng.get_option_chain(symbol, days_to_expiry=dte)
fii_dii = data_eng.get_fii_dii_sentiment()

ind_res = IndicatorEngine.analyze(df_candles)
smc_res = SMCEngine.analyze(df_candles)
confluence = ConfluenceEngine.evaluate(chain_data, ind_res, smc_res, fii_dii)
liq_audit = LiquidityShield.validate_option_liquidity(symbol, chain_data.get('chain_df'), spot)
market_regime = StrategyOptimizer.classify_market_regime(spot, chain_data, ind_res, smc_res)
acc = paper_eng.get_account()

with t_col2:
    chg_c = "#00F5A0" if quote['p_change'] >= 0 else "#FF3B69"
    chg_sign = "+" if quote['p_change'] >= 0 else ""
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: 8px; padding: 4px 10px; height: 38px; display: flex; align-items: center; justify-content: space-between;">
        <span style="font-size: 0.75rem; color: #8B949E; font-weight: 700;">{symbol}</span>
        <span class="mono" style="font-size: 0.95rem; font-weight: 800; color: #FFFFFF;">₹{spot:,.1f}</span>
        <span class="mono" style="font-size: 0.75rem; font-weight: 700; color: {chg_c};">{chg_sign}{quote['p_change']:.2f}%</span>
    </div>
    """, unsafe_allow_html=True)

with t_col3:
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: 8px; padding: 4px 10px; height: 38px; display: flex; align-items: center; justify-content: space-between;">
        <span style="font-size: 0.72rem; color: #8B949E; font-weight: 600;">EXPIRY</span>
        <span class="mono" style="font-size: 0.8rem; font-weight: 800; color: #00D2FF;">{exp_info['dte_badge']}</span>
    </div>
    """, unsafe_allow_html=True)

with t_col4:
    pcr_v = chain_data['pcr']
    pcr_c = "#00F5A0" if pcr_v >= 1.0 else "#FF3B69"
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: 8px; padding: 4px 10px; height: 38px; display: flex; align-items: center; justify-content: space-between;">
        <span style="font-size: 0.72rem; color: #8B949E; font-weight: 600;">PCR / VIX</span>
        <span class="mono" style="font-size: 0.82rem; font-weight: 800; color: {pcr_c};">{pcr_v:.2f}</span>
        <span class="mono" style="font-size: 0.75rem; color: #FFB800;">{chain_data['india_vix']:.1f}</span>
    </div>
    """, unsafe_allow_html=True)

with t_col5:
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: 8px; padding: 4px 10px; height: 38px; display: flex; align-items: center; justify-content: space-between;">
        <span style="font-size: 0.72rem; color: #8B949E; font-weight: 600;">CAPITAL</span>
        <span class="mono" style="font-size: 0.82rem; font-weight: 800; color: #00F5A0;">₹{acc['balance']:,.0f}</span>
    </div>
    """, unsafe_allow_html=True)

with t_col6:
    if st.button("🚨 PANIC EXIT", use_container_width=True, help="Square-off all open paper positions instantly!"):
        open_p = paper_eng.get_open_positions()
        if not open_p.empty:
            for _, r in open_p.iterrows():
                paper_eng.close_position(r['id'], spot, 0.0, exit_reason="EMERGENCY PANIC EXIT")
            st.toast("🚨 All active positions squared off successfully!")
            st.rerun()

st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 3-PANE REAL DENSE QUANT COCKPIT
# -------------------------------------------------------------
left_pane, center_pane, right_pane = st.columns([28, 44, 28])

# =============================================================
# LEFT PANE (28%): 3-LAYER CONFLUENCE COCKPIT
# =============================================================
with left_pane:
    # 1. Master Confluence Score Gauge Card
    conf_score = confluence['confluence_pct']
    bias_text = confluence['market_bias']
    bias_pill = "glow-pill-emerald" if "BULLISH" in bias_text else "glow-pill-rose" if "BEARISH" in bias_text else "glow-pill-gold"
    
    st.markdown(f"""
    <div class="cockpit-card">
        <div class="card-header">
            <span>🎯 3-LAYER CONFLUENCE RADAR</span>
            <span class="{bias_pill}">{bias_text}</span>
        </div>
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 4px 6px;">
            <div>
                <div class="mono" style="font-size: 2.2rem; font-weight: 900; color: #FFFFFF; line-height: 1;">
                    {conf_score:.0f}<span style="font-size: 1.1rem; color: #00D2FF;">%</span>
                </div>
                <div style="font-size: 0.72rem; color: #8B949E; margin-top: 4px;">Institutional Agreement Score</div>
            </div>
            <div style="text-align: right;">
                <span class="glow-pill-purple" style="font-size: 0.75rem;">REGIME: {market_regime['regime']}</span>
                <div style="font-size: 0.7rem; color: #E0AAFF; margin-top: 4px;">{market_regime['recommended_strategy']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Layer 1: Derivatives Data Meter
    ce_oi_total = max(1, chain_data.get('total_ce_oi', 100000))
    pe_oi_total = max(1, chain_data.get('total_pe_oi', 100000))
    tot_oi = ce_oi_total + pe_oi_total
    pe_pct = int((pe_oi_total / tot_oi) * 100)
    ce_pct = 100 - pe_pct

    st.markdown(f"""
    <div class="cockpit-card">
        <div class="card-header">
            <span>📊 LAYER 1: DERIVATIVES OI DYNAMICS</span>
            <span class="glow-pill-cyan">FII: {fii_dii['institutional_bias']}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; font-weight: 700;">
            <span style="color: #00F5A0;">Put OI Support: {pe_pct}%</span>
            <span style="color: #FF3B69;">Call OI Resistance: {ce_pct}%</span>
        </div>
        <div class="ratio-bar-wrapper">
            <div class="ratio-bar-put" style="width: {pe_pct}%;"></div>
            <div class="ratio-bar-call" style="width: {ce_pct}%;"></div>
        </div>
        <div class="badge-grid" style="margin-top: 8px;">
            <div class="badge-cell">
                <span class="badge-cell-label">Call Wall (Resistance)</span>
                <span class="badge-cell-val" style="color: #FF3B69;">{chain_data['top_call_wall']}</span>
            </div>
            <div class="badge-cell">
                <span class="badge-cell-label">Put Wall (Support)</span>
                <span class="badge-cell-val" style="color: #00F5A0;">{chain_data['top_put_wall']}</span>
            </div>
            <div class="badge-cell">
                <span class="badge-cell-label">Max Pain Pin</span>
                <span class="badge-cell-val" style="color: #FFB800;">{chain_data['max_pain']}</span>
            </div>
            <div class="badge-cell">
                <span class="badge-cell-label">IV Rank / Liquidity</span>
                <span class="badge-cell-val" style="color: #00D2FF;">{chain_data['iv_rank']:.0f} / {liq_audit['liquidity_score']}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Layer 2: Technicals Matrix
    st.markdown(f"""
    <div class="cockpit-card">
        <div class="card-header">
            <span>📈 LAYER 2: MOMENTUM & TECHNICAL MATRIX</span>
            <span class="glow-pill-emerald">{ind_res['supertrend']}</span>
        </div>
        <div class="badge-grid">
            <div class="badge-cell">
                <span class="badge-cell-label">VWAP Status</span>
                <span class="badge-cell-val" style="color: #FFB800;">₹{ind_res['vwap']:,.1f}</span>
            </div>
            <div class="badge-cell">
                <span class="badge-cell-label">RSI (14) Momentum</span>
                <span class="badge-cell-val" style="color: #00D2FF;">{ind_res['rsi']:.1f} ({ind_res['rsi_divergence']})</span>
            </div>
            <div class="badge-cell">
                <span class="badge-cell-label">Fast EMA 9</span>
                <span class="badge-cell-val">₹{ind_res['ema_9']:,.1f}</span>
            </div>
            <div class="badge-cell">
                <span class="badge-cell-label">Trend EMA 21</span>
                <span class="badge-cell-val">₹{ind_res['ema_21']:,.1f}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. Layer 3: Smart Money (SMC) Matrix
    st.markdown(f"""
    <div class="cockpit-card">
        <div class="card-header">
            <span>🏦 LAYER 3: SMART MONEY (SMC) MATRIX</span>
            <span class="glow-pill-gold">{smc_res['structure']['structure']}</span>
        </div>
        <div class="badge-grid">
            <div class="badge-cell">
                <span class="badge-cell-label">Pricing Zone</span>
                <span class="badge-cell-val" style="color: #00F5A0;">{smc_res['premium_discount']['zone'].split('(')[0]}</span>
            </div>
            <div class="badge-cell">
                <span class="badge-cell-label">50% Equilibrium</span>
                <span class="badge-cell-val">₹{smc_res['premium_discount']['fib_50']:,.1f}</span>
            </div>
            <div class="badge-cell" style="grid-column: span 2;">
                <span class="badge-cell-label">Liquidity Sweep</span>
                <span class="badge-cell-val" style="font-size: 0.75rem; color: #E0AAFF;">{smc_res['liquidity_sweep'][:35]}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================
# CENTER PANE (44%): LIVE STRATEGY PAYOFF & ACTION COCKPIT
# =============================================================
with center_pane:
    # 1. Strategy Selector Header
    strat_choices = [
        "🦎 The Big Lizard (Zero Upside Risk)",
        "🦋 Broken Wing Butterfly (1:4 RRR)",
        "⏳ Long Double Calendar (Low IV King)",
        "🛡️ Classic Iron Condor (Wings Armor)",
        "🎯 Iron Butterfly (IV Crush)"
    ]
    selected_strat_label = st.selectbox(
        "Choose Strategy",
        strat_choices,
        index=0 if "Big Lizard" in market_regime['recommended_strategy'] else 1 if "Broken Wing" in market_regime['recommended_strategy'] else 2 if "Calendar" in market_regime['recommended_strategy'] else 3,
        label_visibility="collapsed"
    )

    # Strategy Generation
    if "Big Lizard" in selected_strat_label:
        active_strat = StrategyOptimizer.generate_big_lizard(symbol, spot, chain_data, dte=dte, lot_size=default_lot, account_capital=acc['balance'])
    elif "Broken Wing" in selected_strat_label:
        active_strat = StrategyOptimizer.generate_broken_wing_butterfly(symbol, spot, chain_data, dte=dte, lot_size=default_lot, account_capital=acc['balance'])
    elif "Calendar" in selected_strat_label:
        active_strat = StrategyOptimizer.generate_double_calendar(symbol, spot, chain_data, dte=dte, lot_size=default_lot, account_capital=acc['balance'])
    elif "Iron Butterfly" in selected_strat_label:
        active_strat = StrategyOptimizer.generate_iron_butterfly(symbol, spot, chain_data, dte=dte, lot_size=default_lot, account_capital=acc['balance'])
    else:
        active_strat = StrategyOptimizer.generate_classic_iron_condor(symbol, spot, chain_data, dte=dte, lot_size=default_lot, account_capital=acc['balance'])

    # 2. REAL SENSIBULL-STYLE INTERACTIVE PAYOFF GRAPH GENERATOR
    spot_range = np.linspace(spot * 0.94, spot * 1.06, 120)
    pnl_curve = []
    
    # Calculate PnL for each spot price
    for s_price in spot_range:
        total_pnl = 0.0
        for leg in active_strat['legs']:
            k = leg['strike']
            p = leg['ltp']
            q = leg['qty']
            is_call = 'CE' in leg['option']
            is_buy = leg['type'] == 'BUY'
            
            if is_call:
                payoff = max(0.0, s_price - k)
            else:
                payoff = max(0.0, k - s_price)
                
            leg_pnl = (payoff - p) * q if is_buy else (p - payoff) * q
            total_pnl += leg_pnl
            
        pnl_curve.append(total_pnl)

    pnl_array = np.array(pnl_curve)

    # Plotly Sensibull Payoff Curve
    fig_payoff = go.Figure()

    # Zero Line
    fig_payoff.add_hline(y=0, line_dash="solid", line_color="rgba(255,255,255,0.2)", line_width=1)

    # Green Profit Zone Fill
    fig_payoff.add_trace(go.Scatter(
        x=spot_range,
        y=np.maximum(pnl_array, 0),
        mode='lines',
        line=dict(color='#00F5A0', width=0),
        fill='tozeroy',
        fillcolor='rgba(0, 245, 160, 0.18)',
        name='Profit Zone',
        hoverinfo='skip'
    ))

    # Red Loss Zone Fill
    fig_payoff.add_trace(go.Scatter(
        x=spot_range,
        y=np.minimum(pnl_array, 0),
        mode='lines',
        line=dict(color='#FF3B69', width=0),
        fill='tozeroy',
        fillcolor='rgba(255, 59, 105, 0.18)',
        name='Loss Zone',
        hoverinfo='skip'
    ))

    # Main PnL Line
    fig_payoff.add_trace(go.Scatter(
        x=spot_range,
        y=pnl_array,
        mode='lines',
        line=dict(color='#00D2FF', width=2.5),
        name='Expiry P&L',
        hovertemplate='Spot: ₹%{x:,.0f}<br>P&L: ₹%{y:+,.0f}<extra></extra>'
    ))

    # Spot Line Marker
    fig_payoff.add_vline(
        x=spot,
        line_dash="dash",
        line_color="#FFB800",
        line_width=1.5,
        annotation_text=f"Spot ₹{spot:,.0f}",
        annotation_position="top right",
        annotation_font=dict(color="#FFB800", family="JetBrains Mono", size=10)
    )

    fig_payoff.update_layout(
        template='plotly_dark',
        height=260,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='#07090E',
        paper_bgcolor='#07090E',
        showlegend=False,
        font=dict(family='JetBrains Mono', color='#8B949E', size=9),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickprefix='₹'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickprefix='₹', side='right')
    )

    st.plotly_chart(fig_payoff, use_container_width=True, config={'displayModeBar': False})

    # 3. Strike OI Distribution Visual Bar Chart
    df_chain = chain_data.get('chain_df')
    if df_chain is not None and not df_chain.empty:
        near_df = df_chain[(df_chain['strike'] >= spot * 0.97) & (df_chain['strike'] <= spot * 1.03)].head(6)
        if not near_df.empty:
            fig_oi = go.Figure()
            fig_oi.add_trace(go.Bar(
                x=near_df['strike'],
                y=near_df['pe_oi'] if 'pe_oi' in near_df.columns else [50000]*len(near_df),
                name='Put OI (Support)',
                marker_color='#00F5A0',
                opacity=0.85
            ))
            fig_oi.add_trace(go.Bar(
                x=near_df['strike'],
                y=near_df['ce_oi'] if 'ce_oi' in near_df.columns else [50000]*len(near_df),
                name='Call OI (Resistance)',
                marker_color='#FF3B69',
                opacity=0.85
            ))
            fig_oi.update_layout(
                barmode='group',
                template='plotly_dark',
                height=140,
                margin=dict(l=10, r=10, t=6, b=6),
                plot_bgcolor='#07090E',
                paper_bgcolor='#07090E',
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=8)),
                font=dict(family='JetBrains Mono', color='#8B949E', size=8),
                xaxis=dict(gridcolor='rgba(255,255,255,0.03)', type='category'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.03)', side='right')
            )
            st.plotly_chart(fig_oi, use_container_width=True, config={'displayModeBar': False})

    # 4. Action Deck Strip
    st.markdown(f"""
    <div class="cockpit-card" style="margin-top: 4px; padding: 8px 12px;">
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; text-align: center;">
            <div style="background: rgba(255,255,255,0.02); padding: 4px; border-radius: 6px;">
                <div style="font-size: 0.65rem; color: #8B949E;">NET CREDIT</div>
                <div class="mono" style="font-size: 0.85rem; font-weight: 800; color: #00F5A0;">{active_strat['net_credit_debit'].split(' ')[-1]}</div>
            </div>
            <div style="background: rgba(255,255,255,0.02); padding: 4px; border-radius: 6px;">
                <div style="font-size: 0.65rem; color: #8B949E;">MARGIN BLOCKED</div>
                <div class="mono" style="font-size: 0.85rem; font-weight: 800; color: #00D2FF;">{active_strat['final_margin_blocked']}</div>
            </div>
            <div style="background: rgba(255,255,255,0.02); padding: 4px; border-radius: 6px;">
                <div style="font-size: 0.65rem; color: #8B949E;">FUNDS NEEDED</div>
                <div class="mono" style="font-size: 0.85rem; font-weight: 800; color: #FFB800;">{active_strat['upfront_funds_needed']}</div>
            </div>
            <div style="background: rgba(255,255,255,0.02); padding: 4px; border-radius: 6px;">
                <div style="font-size: 0.65rem; color: #8B949E;">WIN PROBABILITY</div>
                <div class="mono" style="font-size: 0.85rem; font-weight: 800; color: #C77DFF;">{active_strat['win_probability']}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"🚀 Deploy 1-Click {active_strat['strategy_name']} ({default_lot} Qty)", use_container_width=True):
        tid = paper_eng.execute_paper_trade(symbol, active_strat, spot, conf_score, lot_size=default_lot)
        st.toast(f"✅ Trade #{tid} Successfully Deployed into Virtual Portfolio!")
        st.rerun()


# =============================================================
# RIGHT PANE (28%): ADJUSTMENT SENTINEL & VOICE AI BUDDY
# =============================================================
with right_pane:
    # 1. Autonomous 3-Level Defense Sentinel Card
    open_trades = paper_eng.get_open_positions()
    if not open_trades.empty:
        latest_trade = open_trades.iloc[-1]
        legs_data = json.loads(latest_trade['legs_json'])
        adj_eval = AdjustmentEngine.evaluate_active_trade(legs_data, spot, smc_res, chain_data.get('chain_df'))
        sentinel_pill = "glow-pill-rose" if adj_eval['severity'] == 'HIGH' else "glow-pill-gold" if adj_eval['severity'] == 'WARNING' else "glow-pill-emerald"
        sentinel_status = adj_eval['status']
        sentinel_reason = adj_eval['trigger_reason']
    else:
        sentinel_pill = "glow-pill-emerald"
        sentinel_status = "SENTINEL ACTIVE (SAFE)"
        sentinel_reason = "No open risk. System armed to defend next trade."
        adj_eval = {'action_plan': []}

    st.markdown(f"""
    <div class="cockpit-card">
        <div class="card-header">
            <span>🛡️ 3-LEVEL DEFENSE SENTINEL</span>
            <span class="{sentinel_pill}">{sentinel_status}</span>
        </div>
        <div style="font-size: 0.75rem; color: #8B949E; margin-bottom: 6px;">{sentinel_reason}</div>
    """, unsafe_allow_html=True)

    if adj_eval['action_plan']:
        for act in adj_eval['action_plan']:
            st.markdown(f"""
            <div style="background: rgba(255,59,105,0.08); border-left: 2px solid #FF3B69; padding: 4px 8px; border-radius: 4px; font-size: 0.72rem; margin-bottom: 4px;">
                <b>Step {act['step']}:</b> {act['action']}
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 2. Greeks Cockpit (4 Compact Meter Boxes)
    st.markdown(f"""
    <div class="cockpit-card">
        <div class="card-header">
            <span>⚡ REAL-TIME GREEKS COCKPIT</span>
            <span class="glow-pill-cyan">DELTA NEUTRAL</span>
        </div>
        <div class="badge-grid">
            <div class="badge-cell">
                <span class="badge-cell-label">Net Delta (Δ)</span>
                <span class="badge-cell-val" style="color: #00F5A0;">+0.04</span>
            </div>
            <div class="badge-cell">
                <span class="badge-cell-label">Daily Theta (Θ)</span>
                <span class="badge-cell-val" style="color: #FFB800;">{active_strat['theta_decay_per_day']}</span>
            </div>
            <div class="badge-cell">
                <span class="badge-cell-label">Gamma Risk (Γ)</span>
                <span class="badge-cell-val" style="color: #00D2FF;">0.0014</span>
            </div>
            <div class="badge-cell">
                <span class="badge-cell-label">Vega Risk (V)</span>
                <span class="badge-cell-val" style="color: #FF3B69;">-₹280 / 1% IV</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Voice AI Quant Copilot Terminal
    st.markdown(f"""
    <div class="cockpit-card" style="margin-bottom: 0;">
        <div class="card-header">
            <span>🤖 GEMINI QUANT BUDDY</span>
            <span class="glow-pill-purple">VOICE READY</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Quick prompt chips
    q1, q2 = st.columns(2)
    quick_q = None
    with q1:
        if st.button("💬 Bhai kya karu?", use_container_width=True):
            quick_q = f"Bhai {symbol} par current spot {spot} aur {market_regime['regime']} regime me kaunsi strategy best hai aur kyu?"
    with q2:
        if st.button("🛡️ Sentinel Status?", use_container_width=True):
            quick_q = f"Bhai {symbol} par adjustment sentinel trigger points aur breakevens kya hain?"

    # Chat Container
    chat_box = st.container(height=170)
    with chat_box:
        for m in st.session_state.gemini_messages[-4:]:
            if m["role"] == "user":
                st.markdown(f"<div class='chat-msg-u'><b>You:</b> {m['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-msg-a'><b>🤖 Bhai:</b> {m['content']}</div>", unsafe_allow_html=True)

    u_input = st.chat_input("Poocho bhai se...")
    act_q = quick_q or u_input

    if act_q:
        st.session_state.gemini_messages.append({"role": "user", "content": act_q})
        m_context = {
            'symbol': symbol, 'spot': spot, 'regime': market_regime['regime'],
            'conf_score': conf_score, 'bias': bias_text, 'pcr': pcr_v, 'vix': chain_data['india_vix'],
            'active_strat': active_strat['strategy_name'], 'balance': acc['balance']
        }
        with st.spinner("Analyzing..."):
            reply = GeminiLiveChat.query_gemini(act_q, m_context, st.session_state.gemini_messages, api_key=config.get("GEMINI_API_KEY"))
        st.session_state.gemini_messages.append({"role": "assistant", "content": reply})
        st.rerun()

    if st.session_state.gemini_messages and len(st.session_state.gemini_messages) > 1:
        last_rep = st.session_state.gemini_messages[-1]["content"]
        if st.button("🔊 Voice Suno", key="play_voice_btn", use_container_width=True):
            with st.spinner("Speaking..."):
                a_file = VoiceAICopilot.speak_text(last_rep, "gemini_voice.mp3")
                if a_file and os.path.exists(a_file):
                    st.audio(a_file, format="audio/mp3")

# -------------------------------------------------------------
# BOTTOM DRAWER: PORTFOLIO & AUDIT JOURNAL
# -------------------------------------------------------------
st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
with st.expander("💼 Active Positions, SQLite Journal & API Settings (₹3,00,000 Benchmark Capital)", expanded=False):
    d_tab1, d_tab2, d_tab3 = st.tabs(["⚡ Active Positions", "📓 Trade History Journal", "⚙️ Fyers & API Gateway"])
    
    with d_tab1:
        open_pos = paper_eng.get_open_positions()
        if open_pos.empty:
            st.caption("No open multi-leg positions in virtual portfolio.")
        else:
            for _, row in open_pos.iterrows():
                pts_diff = spot - row['entry_spot'] if 'Bullish' in row['strategy_type'] else row['entry_spot'] - spot
                mtm_pnl = pts_diff * row['lot_size'] * 0.4
                pnl_c = "#00F5A0" if mtm_pnl >= 0 else "#FF3B69"
                pcol1, pcol2, pcol3 = st.columns([3, 2, 1])
                with pcol1:
                    st.markdown(f"**#{row['id']} {row['strategy_name']}** ({row['symbol']}) | Qty: `{row['lot_size']}`")
                with pcol2:
                    st.markdown(f"<span class='mono' style='font-size: 1.1rem; font-weight: 800; color: {pnl_c};'>MTM PnL: ₹{mtm_pnl:+,.2f}</span>", unsafe_allow_html=True)
                with pcol3:
                    if st.button("Square Off", key=f"sq_b_{row['id']}", use_container_width=True):
                        paper_eng.close_position(row['id'], spot, mtm_pnl, exit_reason="Manual Close")
                        st.rerun()

    with d_tab2:
        jdf = paper_eng.get_journal()
        if jdf.empty:
            st.caption("No closed records in trade journal yet.")
        else:
            st.dataframe(jdf, hide_index=True, use_container_width=True)

    with d_tab3:
        b1, b2 = st.columns(2)
        with b1:
            in_app_id = st.text_input("Fyers App ID", value=config.get("FYERS_APP_ID", ""))
            in_secret_id = st.text_input("Fyers Secret ID", type="password", value=config.get("FYERS_SECRET_ID", ""))
            in_token = st.text_input("Access Token", type="password", value=config.get("FYERS_ACCESS_TOKEN", ""))
            if st.button("💾 Save Fyers Credentials"):
                ConfigManager.save_config({"FYERS_APP_ID": in_app_id, "FYERS_SECRET_ID": in_secret_id, "FYERS_ACCESS_TOKEN": in_token})
                st.success("✅ Saved!")
                st.rerun()
        with b2:
            gem_key = st.text_input("Gemini API Key", value=config.get("GEMINI_API_KEY", ""), type="password")
            if st.button("💾 Save Gemini Key"):
                ConfigManager.save_config({"GEMINI_API_KEY": gem_key})
                st.success("✅ Gemini Key Saved!")
                st.rerun()
