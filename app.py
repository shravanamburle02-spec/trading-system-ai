"""
Master Trading System - Prop-Desk Non-Directional Quant Terminal
Integrated with:
- EXPIRY RADAR & DAYS LEFT COUNTDOWN (NIFTY, BANKNIFTY, SENSEX, FINNIFTY, MIDCPNIFTY)
- REAL-TIME LIVE TICKING CLOCK & COUNTDOWN (Client-side JavaScript)
- Margin Needed (Final Blocked Margin) vs Funds Needed (Upfront Required Cash)
- Safe Buffer Cash Remaining (> ₹2,35,000)
- Basket Execution Sequence (Buy Wings First -> Sell Short Legs)
- 5 Strategy Families (The Big Lizard, Broken Wing Butterfly, Long Calendars, Classic Iron Condor, Iron Fly)
- Prop-Desk 3-Level Defense Sentinel (Level 1 Roll, Level 2 Freeze Gamma, Level 3 Hard Exit)
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
    page_title="QUANT CORE | Expiry Radar & Quant Terminal",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Start Auto-Rebalancer Sentinel in background
AutoRebalancerSentinel.start_sentinel(interval_seconds=10)

# Persistent configuration load
config = ConfigManager.get_config()

# Initialize session states
if "gemini_messages" not in st.session_state:
    st.session_state.gemini_messages = [
        {"role": "assistant", "content": "Namaste bhai! Main tera Prop-Desk Non-Directional Quant Architect hoon. Live Expiry Countdown, 'Margin Blocked' vs 'Funds Needed', Basket Order Execution Sequence (Buy Wings First), aur 3-Level Defense Sentinel ke sath active hoon. Poocho!"}
    ]

# -------------------------------------------------------------
# LUXURY OBSIDIAN GLASSMORPHISM CSS & TYPOGRAPHY
# -------------------------------------------------------------
st.markdown("""
<link rel="preconnect" href="https://fonts.gstatic.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">

<style>
    #MainMenu, footer, header { visibility: hidden !important; height: 0px !important; }
    .stDeployButton { display: none !important; }
    .block-container { padding-top: 0.8rem !important; padding-bottom: 2rem !important; }

    :root {
        --bg-obsidian: #06080D;
        --bg-surface: #0D111A;
        --glass-bg: rgba(255, 255, 255, 0.025);
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
        background: radial-gradient(circle at 50% 0%, #0e1424 0%, #06080D 70%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: var(--text-primary) !important;
    }

    .mono {
        font-family: 'JetBrains Mono', monospace !important;
    }

    section[data-testid="stSidebar"] {
        background: #080B12 !important;
        border-right: 1px solid var(--glass-border) !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
    }

    .glass-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.035) 0%, rgba(255, 255, 255, 0.008) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.45);
        margin-bottom: 14px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(0, 210, 255, 0.25);
    }

    .hero-banner {
        background: linear-gradient(135deg, rgba(0, 210, 255, 0.08) 0%, rgba(0, 245, 160, 0.05) 50%, rgba(157, 78, 221, 0.08) 100%);
        border: 1px solid rgba(0, 210, 255, 0.25);
        border-radius: 16px;
        padding: 18px 24px;
        margin-bottom: 16px;
        box-shadow: 0 0 35px rgba(0, 210, 255, 0.12);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }

    .metric-box {
        background: rgba(13, 17, 26, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 14px 18px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    .metric-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--text-muted);
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.35rem;
        font-weight: 800;
        color: #FFFFFF;
        white-space: nowrap;
        overflow: visible;
    }
    .metric-delta-pos {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--neon-emerald);
        display: flex;
        align-items: center;
        gap: 4px;
        margin-top: 4px;
    }
    .metric-delta-neg {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--neon-rose);
        display: flex;
        align-items: center;
        gap: 4px;
        margin-top: 4px;
    }

    .glow-pill-emerald {
        background: rgba(0, 245, 160, 0.12);
        color: var(--neon-emerald);
        border: 1px solid rgba(0, 245, 160, 0.35);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 0 10px rgba(0, 245, 160, 0.2);
    }
    .glow-pill-rose {
        background: rgba(255, 59, 105, 0.12);
        color: var(--neon-rose);
        border: 1px solid rgba(255, 59, 105, 0.35);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 0 10px rgba(255, 59, 105, 0.2);
    }
    .glow-pill-cyan {
        background: rgba(0, 210, 255, 0.12);
        color: var(--neon-cyan);
        border: 1px solid rgba(0, 210, 255, 0.35);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.2);
    }
    .glow-pill-gold {
        background: rgba(255, 184, 0, 0.12);
        color: var(--neon-gold);
        border: 1px solid rgba(255, 184, 0, 0.35);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 0 10px rgba(255, 184, 0, 0.2);
    }
    .glow-pill-purple {
        background: rgba(157, 78, 221, 0.15);
        color: #C77DFF;
        border: 1px solid rgba(157, 78, 221, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 0 10px rgba(157, 78, 221, 0.25);
    }

    .param-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 7px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        font-size: 0.85rem;
    }
    .param-label {
        color: var(--text-muted);
        font-weight: 500;
    }
    .param-val {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        color: #FFFFFF;
    }

    .custom-progress-bg {
        background: rgba(255, 255, 255, 0.08);
        height: 6px;
        border-radius: 6px;
        overflow: hidden;
        margin: 10px 0 16px 0;
    }
    .custom-progress-fill-emerald {
        background: linear-gradient(90deg, #00D2FF, #00F5A0);
        height: 100%;
        border-radius: 6px;
        box-shadow: 0 0 10px #00F5A0;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(13, 17, 26, 0.8);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid var(--glass-border);
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 8px;
        color: var(--text-muted) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0 18px !important;
        background: transparent !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 210, 255, 0.18) 0%, rgba(0, 245, 160, 0.12) 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(0, 210, 255, 0.35) !important;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.15) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #00D2FF 0%, #00F5A0 100%) !important;
        color: #06080D !important;
        font-weight: 800 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 0 20px rgba(0, 245, 160, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 0 30px rgba(0, 245, 160, 0.6) !important;
    }

    .chat-bubble-user {
        background: rgba(0, 210, 255, 0.12);
        border: 1px solid rgba(0, 210, 255, 0.3);
        padding: 12px 16px;
        border-radius: 12px 12px 2px 12px;
        margin-bottom: 10px;
        color: #FFFFFF;
        font-size: 0.92rem;
    }
    .chat-bubble-ai {
        background: rgba(13, 17, 26, 0.85);
        border: 1px solid rgba(0, 245, 160, 0.25);
        padding: 14px 18px;
        border-radius: 12px 12px 12px 2px;
        margin-bottom: 12px;
        color: #F0F4F8;
        font-size: 0.92rem;
        line-height: 1.5;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# REAL-TIME LIVE TICKING JAVASCRIPT CLOCK COMPONENT
# -------------------------------------------------------------
clock_html = """
<div id="live-clock-wrapper" style="
    background: linear-gradient(135deg, rgba(13, 17, 26, 0.95) 0%, rgba(6, 8, 13, 0.95) 100%);
    border: 1px solid rgba(0, 210, 255, 0.25);
    border-radius: 12px;
    padding: 10px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #F0F4F8;
    box-shadow: 0 4px 25px rgba(0, 0, 0, 0.5);
    margin-bottom: 8px;
">
    <div style="display: flex; align-items: center; gap: 14px;">
        <span style="font-size: 1.05rem; font-weight: 800; color: #FFFFFF; display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-block; width: 8px; height: 8px; background: #00F5A0; border-radius: 50%; box-shadow: 0 0 10px #00F5A0;"></span>
            🇮🇳 NSE & BSE LIVE
        </span>
        <span id="live-date" style="color: #8B949E; font-size: 0.85rem; font-weight: 600;">--</span>
        <span id="live-time" style="font-family: 'Consolas', 'Courier New', monospace; color: #00D2FF; font-weight: 800; font-size: 1.1rem; letter-spacing: 0.5px;">--:--:-- --</span>
    </div>
    <div style="display: flex; align-items: center; gap: 12px;">
        <span id="market-status-pill" style="padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.5px;">CHECKING...</span>
        <span id="live-countdown" style="font-family: 'Consolas', 'Courier New', monospace; color: #FFB800; font-weight: 700; font-size: 0.88rem;">⏳ --</span>
    </div>
</div>

<script>
function updateClock() {
    const now = new Date();
    const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
    const ist = new Date(utc + (3600000 * 5.5));

    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
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
        pill.style.boxShadow = '0 0 10px rgba(255, 59, 105, 0.2)';
        countdown.innerText = '⏳ Opens Monday at 09:15:00 AM';
    } else if (totalMinutes < 540) {
        pill.innerText = '● MARKET CLOSED';
        pill.style.background = 'rgba(255, 59, 105, 0.15)';
        pill.style.color = '#FF3B69';
        pill.style.border = '1px solid rgba(255, 59, 105, 0.4)';
        pill.style.boxShadow = '0 0 10px rgba(255, 59, 105, 0.2)';
        
        const targetSec = 9 * 3600 + 15 * 60;
        const diffSec = targetSec - totalSeconds;
        const h = Math.floor(diffSec / 3600);
        const m = Math.floor((diffSec % 3600) / 60);
        const s = diffSec % 60;
        countdown.innerText = `⏳ Opens in ${String(h).padStart(2,'0')}h ${String(m).padStart(2,'0')}m ${String(s).padStart(2,'0')}s (09:15 AM)`;
    } else if (totalMinutes >= 540 && totalMinutes < 555) {
        pill.innerText = '● PRE-OPEN SESSION';
        pill.style.background = 'rgba(255, 184, 0, 0.15)';
        pill.style.color = '#FFB800';
        pill.style.border = '1px solid rgba(255, 184, 0, 0.4)';
        pill.style.boxShadow = '0 0 10px rgba(255, 184, 0, 0.2)';
        
        const targetSec = 9 * 3600 + 15 * 60;
        const diffSec = targetSec - totalSeconds;
        const m = Math.floor(diffSec / 60);
        const s = diffSec % 60;
        countdown.innerText = `⏳ Live Trading in ${String(m).padStart(2,'0')}m ${String(s).padStart(2,'0')}s`;
    } else if (totalMinutes >= 555 && totalMinutes < 930) {
        pill.innerText = '● MARKET LIVE OPEN';
        pill.style.background = 'rgba(0, 245, 160, 0.15)';
        pill.style.color = '#00F5A0';
        pill.style.border = '1px solid rgba(0, 245, 160, 0.4)';
        pill.style.boxShadow = '0 0 10px rgba(0, 245, 160, 0.2)';
        
        const targetSec = 15 * 3600 + 30 * 60;
        const diffSec = targetSec - totalSeconds;
        const h = Math.floor(diffSec / 3600);
        const m = Math.floor((diffSec % 3600) / 60);
        const s = diffSec % 60;
        countdown.innerText = `⏳ Closes in ${String(h).padStart(2,'0')}h ${String(m).padStart(2,'0')}m ${String(s).padStart(2,'0')}s (03:30 PM)`;
    } else {
        pill.innerText = '● MARKET CLOSED';
        pill.style.background = 'rgba(255, 59, 105, 0.15)';
        pill.style.color = '#FF3B69';
        pill.style.border = '1px solid rgba(255, 59, 105, 0.4)';
        pill.style.boxShadow = '0 0 10px rgba(255, 59, 105, 0.2)';
        countdown.innerText = '⏳ Opens Tomorrow at 09:15:00 AM';
    }
}

updateClock();
setInterval(updateClock, 1000);
</script>
"""

# Render Real-time Live Ticking Clock at top
components.html(clock_html, height=62)

# -------------------------------------------------------------
# DATA INGESTION & CONFLUENCE CALCULATIONS
# -------------------------------------------------------------
fyers_app_id = config.get("FYERS_APP_ID", "")
fyers_token = config.get("FYERS_ACCESS_TOKEN", "")

data_eng = DataEngine(fyers_app_id, fyers_token)
paper_eng = PaperTradingEngine()
paper_eng.init_db(default_capital=300000.0)

# Sleek Sidebar (Focused on 5 Primary Indices)
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
        <div style="background: linear-gradient(135deg, #00D2FF, #00F5A0); width: 36px; height: 36px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 20px;">🏛️</div>
        <div>
            <div style="font-weight: 900; font-size: 1.15rem; letter-spacing: 0.5px; color: #FFFFFF;">PROP-DESK QUANT</div>
            <div style="font-size: 0.72rem; color: #00D2FF; font-weight: 700; letter-spacing: 1px;">EXPIRY & MARGIN SHIELD</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    symbol = st.selectbox(
        "🎯 Select Index Asset",
        ["NIFTY", "BANKNIFTY", "SENSEX", "FINNIFTY", "MIDCPNIFTY", "RELIANCE", "HDFCBANK", "INFY", "TCS", "ASIANPAINT"],
        index=0
    )

    # Dynamic Expiry Calculation for Selected Symbol
    exp_info = LiquidityShield.get_detailed_expiry_info(symbol)
    dte = exp_info['days_left']

    # Sidebar Expiry Card
    st.markdown(f"""
    <div class="glass-card" style="padding: 12px 14px; margin-bottom: 14px; border-left: 3px solid #00D2FF;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-size: 0.75rem; color: #8B949E; font-weight: 700; text-transform: uppercase;">Upcoming Expiry</span>
            <span class="glow-pill-cyan">{exp_info['expiry_type']}</span>
        </div>
        <div class="mono" style="font-size: 1.05rem; font-weight: 800; color: #FFFFFF;">{exp_info['expiry_date_str']}</div>
        <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 6px;">
            <span style="font-size: 0.8rem; color: #00F5A0; font-weight: 800;">{exp_info['dte_badge']}</span>
            <span class="mono" style="font-size: 0.75rem; color: #FFB800;">⏳ {exp_info['countdown_str']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    default_lot = DataEngine.LOT_SIZES.get(symbol, 75)
    lot_size = st.number_input(f"📦 Position Qty (1 Lot = {default_lot})", value=default_lot, step=default_lot)

    st.markdown("<hr style='border-color: rgba(255,255,255,0.06);'>", unsafe_allow_html=True)
    
    # Connection Status Pill
    if data_eng.fyers.is_connected():
        st.markdown("<div class='glow-pill-emerald' style='width: 100%; justify-content: center; margin-bottom: 8px;'>🟢 FYERS API V3 CONNECTED</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='glow-pill-cyan' style='width: 100%; justify-content: center; margin-bottom: 8px;'>🔵 SIMULATED / NSE FEED</div>", unsafe_allow_html=True)

    # Sentinel Daemon Status
    st.markdown("<div class='glow-pill-emerald' style='width: 100%; justify-content: center; margin-bottom: 8px;'>🛡️ 3-LEVEL SENTINEL: ON</div>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color: rgba(255,255,255,0.06);'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 0.75rem; text-transform: uppercase; color: #8B949E; font-weight: 700; margin-bottom: 8px;'>Virtual Portfolio (₹3L Cap)</div>", unsafe_allow_html=True)
    
    acc = paper_eng.get_account()
    pnl_color = "#00F5A0" if acc['realized_pnl'] >= 0 else "#FF3B69"
    st.markdown(f"""
    <div class="glass-card" style="padding: 12px 14px; margin-bottom: 12px;">
        <div style="font-size: 0.75rem; color: #8B949E;">Active Capital Balance</div>
        <div class="mono" style="font-size: 1.2rem; font-weight: 800; color: #FFFFFF;">₹{acc['balance']:,.2f}</div>
        <div class="mono" style="font-size: 0.8rem; font-weight: 700; color: {pnl_color}; margin-top: 4px;">
            {acc['realized_pnl']:+,.2f} ({acc['return_pct']:+.2f}%)
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 Sync Live Feed", use_container_width=True):
        st.rerun()

# Fetch Stack
quote = data_eng.get_market_quote(symbol)
spot = quote['current_price']
df_candles = quote['df']
chain_data = data_eng.get_option_chain(symbol, days_to_expiry=dte)
fii_dii = data_eng.get_fii_dii_sentiment()

# Compute Engines
ind_res = IndicatorEngine.analyze(df_candles)
smc_res = SMCEngine.analyze(df_candles)
confluence = ConfluenceEngine.evaluate(chain_data, ind_res, smc_res, fii_dii)

# Liquidity Audit
liq_audit = LiquidityShield.validate_option_liquidity(symbol, chain_data.get('chain_df'), spot)

# Real-Time Regime Classification
market_regime = StrategyOptimizer.classify_market_regime(spot, chain_data, ind_res, smc_res)

# Pre-Compute Prop-Desk Strategy Suite with Margin & Funds Needed
strat_big_lizard = StrategyOptimizer.generate_big_lizard(symbol, spot, chain_data, dte=dte, lot_size=lot_size, account_capital=acc['balance'])
strat_bwb = StrategyOptimizer.generate_broken_wing_butterfly(symbol, spot, chain_data, dte=dte, lot_size=lot_size, account_capital=acc['balance'])
strat_calendar = StrategyOptimizer.generate_double_calendar(symbol, spot, chain_data, dte=dte, lot_size=lot_size, account_capital=acc['balance'])
strat_condor = StrategyOptimizer.generate_classic_iron_condor(symbol, spot, chain_data, dte=dte, lot_size=lot_size, account_capital=acc['balance'])
strat_butterfly = StrategyOptimizer.generate_iron_butterfly(symbol, spot, chain_data, dte=dte, lot_size=lot_size, account_capital=acc['balance'])

# Comprehensive Institutional Market Context for Gemini
market_context_dict = {
    'symbol': symbol,
    'spot': spot,
    'expiry_date': exp_info['expiry_date_str'],
    'expiry_type': exp_info['expiry_type'],
    'days_to_expiry': exp_info['days_left'],
    'expiry_countdown': exp_info['countdown_str'],
    'change': f"{quote['p_change']:+.2f}%",
    'day_low': df_candles['Low'].min(),
    'day_high': df_candles['High'].max(),
    'lot_size': DataEngine.LOT_SIZES.get(symbol, 75),
    'confluence_pct': confluence['confluence_pct'],
    'market_bias': confluence['market_bias'],
    'agreement_status': confluence['agreement_status'],
    'strat_mode': 'Prop-Desk Masterclass Non-Directional',
    'market_regime': market_regime['regime'],
    'recommended_strategy': market_regime['recommended_strategy'],
    'pcr': chain_data['pcr'],
    'max_pain': chain_data['max_pain'],
    'atm_iv': chain_data['atm_iv'],
    'iv_rank': chain_data['iv_rank'],
    'vix': chain_data['india_vix'],
    'top_call_wall': chain_data['top_call_wall'],
    'top_put_wall': chain_data['top_put_wall'],
    'fii_bias': fii_dii['institutional_bias'],
    'fii_net': fii_dii['fii_net_index_futures'],
    'vwap': ind_res['vwap'],
    'vwap_status': ind_res['vwap_status'],
    'rsi': ind_res['rsi'],
    'rsi_divergence': ind_res['rsi_divergence'],
    'ema_9': ind_res['ema_9'],
    'ema_21': ind_res['ema_21'],
    'ema_50': ind_res['ema_50'],
    'supertrend': ind_res['supertrend'],
    'structure': smc_res['structure']['structure'],
    'zone': smc_res['premium_discount']['zone'],
    'fib_50': smc_res['premium_discount']['fib_50'],
    'order_block': 'Demand OB Valid' if 'BULLISH' in confluence['market_bias'] else 'Supply OB Valid',
    'liquidity': smc_res['liquidity_sweep'],
    'strategy_name': strat_condor['strategy_name'],
    'win_prob': strat_condor['win_probability'],
    'target_1': strat_condor['target_1'],
    'stop_loss': strat_condor['max_loss'],
    'balance': acc['balance']
}

# -------------------------------------------------------------
# HERO BANNER: MASTER REGIME CLASSIFICATION & EXPIRY RADAR
# -------------------------------------------------------------
st.markdown(f"""
<div class="hero-banner">
    <div style="display: flex; align-items: center; gap: 20px;">
        <div style="background: radial-gradient(circle, rgba(0,210,255,0.2) 0%, rgba(0,0,0,0) 70%); border: 2px solid #00F5A0; width: 72px; height: 72px; border-radius: 50%; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 0 20px #00F5A040;">
            <span class="mono" style="font-size: 1.25rem; font-weight: 900; color: #FFFFFF; line-height: 1;">{strat_condor['win_probability']}</span>
            <span style="font-size: 0.6rem; color: #8B949E; font-weight: 700; text-transform: uppercase;">Win Prob</span>
        </div>
        <div>
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                <span class="glow-pill-purple">REGIME: {market_regime['regime']}</span>
                <span class="glow-pill-cyan">EXPIRY: {exp_info['expiry_date_str']}</span>
                <span class="glow-pill-gold">⚡ {exp_info['dte_badge']} ({exp_info['countdown_str']})</span>
            </div>
            <div style="font-size: 1.2rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.3px;">
                Recommended: {market_regime['recommended_strategy']}
            </div>
            <div style="font-size: 0.82rem; color: #00D2FF; margin-top: 2px;">
                {market_regime['reason']}
            </div>
        </div>
    </div>
    <div style="text-align: right;">
        <div style="font-size: 0.75rem; color: #8B949E; text-transform: uppercase; font-weight: 600;">Optimal Breakevens</div>
        <div class="mono" style="font-size: 1.1rem; font-weight: 800; color: #00F5A0; margin-top: 2px;">
            {strat_condor['lower_breakeven']} — {strat_condor['upper_breakeven']}
        </div>
        <div style="font-size: 0.75rem; color: #8B949E;">Spot Anchor: ₹{spot:,.2f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# TOP METRICS ROW: CUSTOM LUXURY BOXES
# -------------------------------------------------------------
mcol1, mcol2, mcol3, mcol4, mcol5, mcol6 = st.columns(6)

with mcol1:
    delta_class = "metric-delta-pos" if quote['p_change'] >= 0 else "metric-delta-neg"
    delta_sign = "+" if quote['p_change'] >= 0 else ""
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">{symbol} SPOT</div>
        <div class="metric-value">₹{spot:,.2f}</div>
        <div class="{delta_class}">{delta_sign}{quote['change']:,.2f} ({delta_sign}{quote['p_change']:.2f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with mcol2:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">EXPIRY COUNTDOWN</div>
        <div class="metric-value" style="color: #00D2FF; font-size: 1.15rem;">{exp_info['dte_badge']}</div>
        <div style="font-size: 0.75rem; color: #FFB800; margin-top: 4px;">{exp_info['countdown_str']}</div>
    </div>
    """, unsafe_allow_html=True)

with mcol3:
    pcr_val = chain_data['pcr']
    pcr_status = "Bullish Grip" if pcr_val > 1.05 else "Bearish Grip" if pcr_val < 0.90 else "Neutral Range"
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">PCR (PUT/CALL)</div>
        <div class="metric-value">{pcr_val:.2f}</div>
        <div class="metric-delta-pos">Range: {pcr_status}</div>
    </div>
    """, unsafe_allow_html=True)

with mcol4:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">MAX PAIN PIN</div>
        <div class="metric-value">{chain_data['max_pain']}</div>
        <div style="font-size: 0.78rem; color: #8B949E; margin-top: 4px;">Expiry Anchor</div>
    </div>
    """, unsafe_allow_html=True)

with mcol5:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">ATM IV / IVR</div>
        <div class="metric-value">{chain_data['atm_iv']:.1f}%</div>
        <div style="font-size: 0.78rem; color: #00D2FF; margin-top: 4px;">IV Rank: {chain_data['iv_rank']:.1f}</div>
    </div>
    """, unsafe_allow_html=True)

with mcol6:
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-label">INDIA VIX</div>
        <div class="metric-value">{chain_data['india_vix']:.2f}</div>
        <div style="font-size: 0.78rem; color: #FFB800; margin-top: 4px;">Regime: Volatility</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# MAIN TRADING TERMINAL TABS
# -------------------------------------------------------------
tabs = st.tabs([
    "🎯 3-Layer Confluence Matrix",
    "🏛️ Prop-Desk Master Strategy Suite",
    "🛡️ Autonomous 3-Level Defense Sentinel",
    "📈 Paper Trading & Auto-Journal",
    "💬 Gemini Quant Copilot",
    "⚙️ Fyers & API Gateway"
])

# -------------------------------------------------------------
# TAB 1: 3-LAYER CONFLUENCE MATRIX
# -------------------------------------------------------------
with tabs[0]:
    c1, c2, c3 = st.columns(3)

    with c1:
        d_score = confluence['layer_scores']['data_score']
        d_fill = "custom-progress-fill-emerald"
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-weight: 800; font-size: 1.05rem; color: #FFFFFF;">📊 Layer 1: Derivatives</div>
                <span class="glow-pill-emerald">{d_score:+d} / 100</span>
            </div>
            <div class="custom-progress-bg">
                <div class="{d_fill}" style="width: {max(15, abs(d_score))}%;"></div>
            </div>
            <div class="param-row"><span class="param-label">Call Wall (Resistance)</span><span class="param-val" style="color: #FF3B69;">{chain_data['top_call_wall']}</span></div>
            <div class="param-row"><span class="param-label">Put Wall (Support)</span><span class="param-val" style="color: #00F5A0;">{chain_data['top_put_wall']}</span></div>
            <div class="param-row"><span class="param-label">Total Call OI</span><span class="param-val">{chain_data['total_ce_oi']:,}</span></div>
            <div class="param-row"><span class="param-label">Total Put OI</span><span class="param-val">{chain_data['total_pe_oi']:,}</span></div>
            <div class="param-row" style="border-bottom: none;"><span class="param-label">Institutional Bias</span><span class="param-val" style="color: #00D2FF;">{fii_dii['institutional_bias']}</span></div>
            <div style="margin-top: 14px; font-size: 0.78rem;">
        """, unsafe_allow_html=True)
        for r in confluence['all_reasons']['data_reasons']:
            st.markdown(f"<div style='color: #8B949E; margin-bottom: 4px;'>• {r}</div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    with c2:
        i_score = confluence['layer_scores']['indicator_score']
        i_fill = "custom-progress-fill-emerald"
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-weight: 800; font-size: 1.05rem; color: #FFFFFF;">📈 Layer 2: Technicals</div>
                <span class="glow-pill-emerald">{i_score:+d} / 100</span>
            </div>
            <div class="custom-progress-bg">
                <div class="{i_fill}" style="width: {max(15, abs(i_score))}%;"></div>
            </div>
            <div class="param-row"><span class="param-label">VWAP Level</span><span class="param-val">₹{ind_res['vwap']:,.2f} ({ind_res['vwap_status']})</span></div>
            <div class="param-row"><span class="param-label">RSI (14) Momentum</span><span class="param-val" style="color: #00D2FF;">{ind_res['rsi']:.1f}</span></div>
            <div class="param-row"><span class="param-label">RSI Divergence</span><span class="param-val">{ind_res['rsi_divergence']}</span></div>
            <div class="param-row"><span class="param-label">EMA Ribbon</span><span class="param-val">9={ind_res['ema_9']:.0f} | 21={ind_res['ema_21']:.0f}</span></div>
            <div class="param-row" style="border-bottom: none;"><span class="param-label">Supertrend</span><span class="param-val" style="color: {'#00F5A0' if ind_res['supertrend']=='Bullish' else '#FF3B69'};">{ind_res['supertrend']}</span></div>
            <div style="margin-top: 14px; font-size: 0.78rem;">
        """, unsafe_allow_html=True)
        for r in confluence['all_reasons']['indicator_reasons']:
            st.markdown(f"<div style='color: #8B949E; margin-bottom: 4px;'>• {r}</div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    with c3:
        s_score = confluence['layer_scores']['smc_score']
        s_fill = "custom-progress-fill-emerald"
        st.markdown(f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-weight: 800; font-size: 1.05rem; color: #FFFFFF;">🏦 Layer 3: Smart Money</div>
                <span class="glow-pill-emerald">{s_score:+d} / 100</span>
            </div>
            <div class="custom-progress-bg">
                <div class="{s_fill}" style="width: {max(15, abs(s_score))}%;"></div>
            </div>
            <div class="param-row"><span class="param-label">Market Structure</span><span class="param-val" style="color: #00F5A0;">{smc_res['structure']['structure']}</span></div>
            <div class="param-row"><span class="param-label">Pricing Zone</span><span class="param-val">{smc_res['premium_discount']['zone'].split('(')[0]}</span></div>
            <div class="param-row"><span class="param-label">Liquidity Sweep</span><span class="param-val" style="font-size: 0.78rem;">{smc_res['liquidity_sweep'][:28]}</span></div>
            <div class="param-row"><span class="param-label">Equilibrium 50%</span><span class="param-val">₹{smc_res['premium_discount']['fib_50']:,.2f}</span></div>
            <div class="param-row" style="border-bottom: none;"><span class="param-label">Order Block</span><span class="param-val" style="color: #00D2FF;">Demand OB Valid</span></div>
            <div style="margin-top: 14px; font-size: 0.78rem;">
        """, unsafe_allow_html=True)
        for r in confluence['all_reasons']['smc_reasons']:
            st.markdown(f"<div style='color: #8B949E; margin-bottom: 4px;'>• {r}</div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    # Candlestick Chart
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    fig = go.Figure(data=[go.Candlestick(
        x=df_candles.index,
        open=df_candles['Open'],
        high=df_candles['High'],
        low=df_candles['Low'],
        close=df_candles['Close'],
        increasing_line_color='#00F5A0',
        decreasing_line_color='#FF3B69',
        name='Spot Price'
    )])
    fig.add_trace(go.Scatter(x=df_candles.index, y=ind_res['df_indicators']['VWAP'], mode='lines', name='VWAP', line=dict(color='#FFB800', width=1.5)))
    fig.add_trace(go.Scatter(x=df_candles.index, y=ind_res['df_indicators']['EMA_9'], mode='lines', name='9 EMA Fast', line=dict(color='#00D2FF', width=1)))
    fig.add_trace(go.Scatter(x=df_candles.index, y=ind_res['df_indicators']['EMA_21'], mode='lines', name='21 EMA Trend', line=dict(color='#9D4EDD', width=1)))
    
    fig.update_layout(
        template='plotly_dark',
        height=460,
        margin=dict(l=15, r=15, t=30, b=15),
        plot_bgcolor='#07090E',
        paper_bgcolor='#07090E',
        xaxis_rangeslider_visible=False,
        font=dict(family='JetBrains Mono', color='#8B949E'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)', side='right')
    )
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------
# TAB 2: PROP-DESK MASTER STRATEGY SUITE (MARGIN & FUNDS SHIELD)
# -------------------------------------------------------------
with tabs[1]:
    st.markdown(f"### 🏛️ Prop-Desk Masterclass Strategy Suite ({symbol})")
    st.markdown(f"""
    <div style="background: rgba(157, 78, 221, 0.1); border: 1px solid rgba(157, 78, 221, 0.35); padding: 12px 16px; border-radius: 12px; margin-bottom: 16px;">
        <div style="font-weight: 800; color: #C77DFF; font-size: 0.95rem;">🎯 ACTIVE REGIME: {market_regime['regime']} ➔ {market_regime['recommended_strategy']}</div>
        <div style="font-size: 0.82rem; color: #E0AAFF; margin-top: 2px;">{market_regime['reason']} | Expiry Target: <b>{exp_info['expiry_date_str']}</b> ({exp_info['dte_badge']})</div>
    </div>
    """, unsafe_allow_html=True)

    adv_col1, adv_col2 = st.columns(2)

    with adv_col1:
        # STRATEGY 1: THE BIG LIZARD
        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid #00F5A0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-weight: 800; font-size: 1.1rem; color: #FFFFFF;">Strategy 1: The Big Lizard (High-Yield)</div>
                <span class="glow-pill-emerald">Win: {strat_big_lizard['win_probability']}</span>
            </div>
            <div style="display: flex; gap: 8px; margin-bottom: 10px;">
                <span class="glow-pill-purple">Zero Upside Risk</span>
                <span class="glow-pill-cyan">{strat_big_lizard['family']}</span>
            </div>
            <div class="param-row"><span class="param-label">Max Profit (Net Credit)</span><span class="param-val" style="color: #00F5A0;">{strat_big_lizard['max_profit']}</span></div>
            <div class="param-row"><span class="param-label">Capped Risk (Downside Only)</span><span class="param-val" style="color: #FF3B69;">{strat_big_lizard['max_loss']}</span></div>
            <div class="param-row"><span class="param-label">Breakeven</span><span class="param-val" style="color: #00D2FF;">{strat_big_lizard['lower_breakeven']}</span></div>
            <div class="param-row"><span class="param-label">Daily Theta Harvest</span><span class="param-val" style="color: #FFB800;">{strat_big_lizard['theta_decay_per_day']}</span></div>
            <div class="param-row"><span class="param-label">🟢 Final Margin Blocked</span><span class="param-val" style="color: #00F5A0;">{strat_big_lizard['final_margin_blocked']}</span></div>
            <div class="param-row"><span class="param-label">🔵 Upfront Funds Needed</span><span class="param-val" style="color: #00D2FF;">{strat_big_lizard['upfront_funds_needed']}</span></div>
            <div class="param-row" style="border-bottom: none;"><span class="param-label">🛡️ Cash Buffer Left (₹3L Cap)</span><span class="param-val" style="color: #FFB800;">{strat_big_lizard['buffer_cash_remaining']}</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(strat_big_lizard['legs']), hide_index=True, use_container_width=True)
        if st.button("🚀 Deploy The Big Lizard", key="exec_big_lizard", use_container_width=True):
            tid = paper_eng.execute_paper_trade(symbol, strat_big_lizard, spot, confluence['confluence_pct'], lot_size=lot_size)
            st.success(f"✅ Big Lizard #{tid} successfully deployed!")
            st.rerun()

        st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)

        # STRATEGY 3: LONG DOUBLE CALENDAR
        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid #00D2FF;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-weight: 800; font-size: 1.1rem; color: #FFFFFF;">Strategy 3: Long Double Calendar Spread</div>
                <span class="glow-pill-cyan">Win: {strat_calendar['win_probability']}</span>
            </div>
            <div style="display: flex; gap: 8px; margin-bottom: 10px;">
                <span class="glow-pill-gold">Low IV King (IVR < 20)</span>
                <span class="glow-pill-purple">{strat_calendar['family']}</span>
            </div>
            <div class="param-row"><span class="param-label">Max Profit (Time Decay)</span><span class="param-val" style="color: #00F5A0;">{strat_calendar['max_profit']}</span></div>
            <div class="param-row"><span class="param-label">Capped Max Risk (Net Debit)</span><span class="param-val" style="color: #FF3B69;">{strat_calendar['max_loss']}</span></div>
            <div class="param-row"><span class="param-label">Safe Profit Tent</span><span class="param-val">{strat_calendar['lower_breakeven']} — {strat_calendar['upper_breakeven']}</span></div>
            <div class="param-row"><span class="param-label">Daily Theta Harvest</span><span class="param-val" style="color: #FFB800;">{strat_calendar['theta_decay_per_day']}</span></div>
            <div class="param-row"><span class="param-label">🟢 Final Margin Blocked</span><span class="param-val" style="color: #00F5A0;">{strat_calendar['final_margin_blocked']}</span></div>
            <div class="param-row"><span class="param-label">🔵 Upfront Funds Needed</span><span class="param-val" style="color: #00D2FF;">{strat_calendar['upfront_funds_needed']}</span></div>
            <div class="param-row" style="border-bottom: none;"><span class="param-label">🛡️ Cash Buffer Left (₹3L Cap)</span><span class="param-val" style="color: #FFB800;">{strat_calendar['buffer_cash_remaining']}</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(strat_calendar['legs']), hide_index=True, use_container_width=True)
        if st.button("🚀 Deploy Long Double Calendar", key="exec_calendar", use_container_width=True):
            tid = paper_eng.execute_paper_trade(symbol, strat_calendar, spot, confluence['confluence_pct'], lot_size=lot_size)
            st.success(f"✅ Double Calendar #{tid} successfully deployed!")
            st.rerun()

    with adv_col2:
        # STRATEGY 2: BROKEN WING BUTTERFLY (BWB)
        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid #FFB800;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-weight: 800; font-size: 1.1rem; color: #FFFFFF;">Strategy 2: Broken Wing Butterfly (BWB)</div>
                <span class="glow-pill-gold">Win: {strat_bwb['win_probability']}</span>
            </div>
            <div style="display: flex; gap: 8px; margin-bottom: 10px;">
                <span class="glow-pill-purple">1 : 4 Asymmetric RRR</span>
                <span class="glow-pill-emerald">{strat_bwb['family']}</span>
            </div>
            <div class="param-row"><span class="param-label">Max Sweet-Spot Profit</span><span class="param-val" style="color: #00F5A0;">{strat_bwb['max_profit']}</span></div>
            <div class="param-row"><span class="param-label">Capped Risk (Downside)</span><span class="param-val" style="color: #FF3B69;">{strat_bwb['max_loss']}</span></div>
            <div class="param-row"><span class="param-label">Upside Breakeven</span><span class="param-val" style="color: #00D2FF;">{strat_bwb['upper_breakeven']}</span></div>
            <div class="param-row"><span class="param-label">Daily Theta Harvest</span><span class="param-val" style="color: #FFB800;">{strat_bwb['theta_decay_per_day']}</span></div>
            <div class="param-row"><span class="param-label">🟢 Final Margin Blocked</span><span class="param-val" style="color: #00F5A0;">{strat_bwb['final_margin_blocked']}</span></div>
            <div class="param-row"><span class="param-label">🔵 Upfront Funds Needed</span><span class="param-val" style="color: #00D2FF;">{strat_bwb['upfront_funds_needed']}</span></div>
            <div class="param-row" style="border-bottom: none;"><span class="param-label">🛡️ Cash Buffer Left (₹3L Cap)</span><span class="param-val" style="color: #FFB800;">{strat_bwb['buffer_cash_remaining']}</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(strat_bwb['legs']), hide_index=True, use_container_width=True)
        if st.button("🚀 Deploy Broken Wing Butterfly", key="exec_bwb", use_container_width=True):
            tid = paper_eng.execute_paper_trade(symbol, strat_bwb, spot, confluence['confluence_pct'], lot_size=lot_size)
            st.success(f"✅ BWB #{tid} successfully deployed!")
            st.rerun()

        st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)

        # STRATEGY 4: CLASSIC IRON CONDOR (WINGS ARMOR)
        st.markdown(f"""
        <div class="glass-card" style="border-left: 4px solid #9D4EDD;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="font-weight: 800; font-size: 1.1rem; color: #FFFFFF;">Strategy 4: Classic Iron Condor (Wings Armor)</div>
                <span class="glow-pill-purple">Win: {strat_condor['win_probability']}</span>
            </div>
            <div style="display: flex; gap: 8px; margin-bottom: 10px;">
                <span class="glow-pill-cyan">Defined-Risk Armor</span>
                <span class="glow-pill-emerald">{strat_condor['family']}</span>
            </div>
            <div class="param-row"><span class="param-label">Max Profit (Net Credit)</span><span class="param-val" style="color: #00F5A0;">{strat_condor['max_profit']}</span></div>
            <div class="param-row"><span class="param-label">Capped Risk (Both Sides)</span><span class="param-val" style="color: #FF3B69;">{strat_condor['max_loss']}</span></div>
            <div class="param-row"><span class="param-label">Breakeven Range</span><span class="param-val">{strat_condor['lower_breakeven']} — {strat_condor['upper_breakeven']}</span></div>
            <div class="param-row"><span class="param-label">Daily Theta Harvest</span><span class="param-val" style="color: #FFB800;">{strat_condor['theta_decay_per_day']}</span></div>
            <div class="param-row"><span class="param-label">🟢 Final Margin Blocked</span><span class="param-val" style="color: #00F5A0;">{strat_condor['final_margin_blocked']}</span></div>
            <div class="param-row"><span class="param-label">🔵 Upfront Funds Needed</span><span class="param-val" style="color: #00D2FF;">{strat_condor['upfront_funds_needed']}</span></div>
            <div class="param-row" style="border-bottom: none;"><span class="param-label">🛡️ Cash Buffer Left (₹3L Cap)</span><span class="param-val" style="color: #FFB800;">{strat_condor['buffer_cash_remaining']}</span></div>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(strat_condor['legs']), hide_index=True, use_container_width=True)
        if st.button("🚀 Deploy Classic Iron Condor", key="exec_condor", use_container_width=True):
            tid = paper_eng.execute_paper_trade(symbol, strat_condor, spot, confluence['confluence_pct'], lot_size=lot_size)
            st.success(f"✅ Iron Condor #{tid} successfully deployed!")
            st.rerun()

# -------------------------------------------------------------
# TAB 3: PROP-DESK 3-LEVEL DEFENSE SENTINEL
# -------------------------------------------------------------
with tabs[2]:
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
        <div>
            <div style="font-weight: 900; font-size: 1.25rem; color: #FFFFFF;">🛡️ Prop-Desk 3-Level Dynamic Defense Sentinel</div>
            <div style="font-size: 0.82rem; color: #00D2FF;">Level 1 Roll Untested | Level 2 Freeze Gamma | Level 3 Hard Capped Exit | Max 2 Rolls Rule</div>
        </div>
        <span class="glow-pill-emerald">● SENTINEL DAEMON: ACTIVE</span>
    </div>
    """, unsafe_allow_html=True)

    acol1, acol2 = st.columns([3, 1])
    with acol2:
        if st.button("⚡ Run Instant Auto-Scan", use_container_width=True):
            executed = AutoRebalancerSentinel.check_and_adjust_all_positions(data_eng)
            if executed:
                for act in executed:
                    st.success(act)
            else:
                st.info("✅ All positions are safe and delta-neutral. No adjustments needed.")
            st.rerun()

    open_trades = paper_eng.get_open_positions()
    if open_trades.empty:
        st.info("ℹ️ No active multi-leg positions in portfolio. Deploy a Non-Directional setup to activate live background rebalancing.")
    else:
        for _, trade in open_trades.iterrows():
            legs = json.loads(trade['legs_json'])
            adj = AdjustmentEngine.evaluate_active_trade(legs, spot, smc_res, chain_data['chain_df'])
            pill = "glow-pill-rose" if adj['severity']=='HIGH' else "glow-pill-gold" if adj['severity']=='WARNING' else "glow-pill-emerald"
            st.markdown(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 800; font-size: 1.1rem; color: #FFFFFF;">Position #{trade['id']}: {trade['strategy_name']} ({trade['symbol']})</div>
                    <span class="{pill}">Trigger: {adj['status']}</span>
                </div>
                <div style="font-size: 0.85rem; color: #8B949E; margin-bottom: 12px;">{adj['trigger_reason']}</div>
            """, unsafe_allow_html=True)
            if adj['action_plan']:
                st.markdown("<div style='font-weight: 700; color: #00D2FF; margin-bottom: 6px;'>Prop-Desk Defense Protocol:</div>", unsafe_allow_html=True)
                for act in adj['action_plan']:
                    st.markdown(f"<div style='background: rgba(255,255,255,0.03); padding: 8px 12px; border-radius: 8px; margin-bottom: 6px; font-size: 0.85rem;'><b>Step {act['step']}:</b> {act['action']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # Autonomous Adjustment Audit Trail
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 📋 Autonomous Defensive Execution Audit Log")
    adj_logs = paper_eng.get_adjustment_logs()
    if adj_logs.empty:
        st.caption("No adjustments executed yet. System will automatically log rolls and hedge actions here.")
    else:
        st.dataframe(adj_logs, hide_index=True, use_container_width=True)

    st.divider()

    st.markdown("### 🔒 Hard Capital Guardrails & Economic Event Shield")
    rcol1, rcol2 = st.columns(2)
    with rcol1:
        sizing = RiskShield.calculate_lot_size(acc['balance'], risk_per_trade_pct=1.5, per_lot_risk=1500, vix=chain_data['india_vix'])
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-weight: 800; font-size: 1.05rem; color: #FFFFFF; margin-bottom: 10px;">📊 Dynamic Position Sizing</div>
            <div class="param-row"><span class="param-label">Account Capital</span><span class="param-val">₹{sizing['account_capital']:,.2f}</span></div>
            <div class="param-row"><span class="param-label">Max Risk Per Trade (1.5%)</span><span class="param-val" style="color: #FF3B69;">₹{sizing['risk_per_trade_inr']:,.2f}</span></div>
            <div class="param-row"><span class="param-label">Recommended Lot Sizing</span><span class="param-val" style="color: #00F5A0;">{sizing['recommended_lots']} Lots</span></div>
            <div class="param-row" style="border-bottom: none;"><span class="param-label">VIX Volatility Dampener</span><span class="param-val">{sizing['vix_adjustment_factor']}</span></div>
        </div>
        """, unsafe_allow_html=True)

    with rcol2:
        events = RiskShield.get_event_shield_status()
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-weight: 800; font-size: 1.05rem; color: #FFFFFF; margin-bottom: 10px;">📅 Macro Event Shield</div>
            <div class="glow-pill-gold" style="margin-bottom: 8px;">{events['event_status']}</div>
            <div style="font-size: 0.82rem; color: #8B949E; line-height: 1.4;">{events['warning']}</div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 4: 3-5 MONTH PAPER TRADING & AUTO-JOURNAL
# -------------------------------------------------------------
with tabs[3]:
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
        <div>
            <div style="font-weight: 900; font-size: 1.25rem; color: #FFFFFF;">📈 3-5 Month Paper Trading Incubation & Performance Engine</div>
            <div style="font-size: 0.82rem; color: #00D2FF;">Benchmark Capital: ₹3,00,000 | 1.5% Risk Control | Statistical Win-Rate & Strategy Journal</div>
        </div>
        <span class="glow-pill-cyan">PHASE: PAPER INCUBATION (3-5M)</span>
    </div>
    """, unsafe_allow_html=True)

    jdf = paper_eng.get_journal()
    total_trades = len(jdf)
    winning_trades = len(jdf[jdf['pnl'] > 0]) if not jdf.empty else 0
    win_rate = round((winning_trades / total_trades * 100), 1) if total_trades > 0 else 0.0

    pcol1, pcol2, pcol3, pcol4 = st.columns(4)
    with pcol1:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">VIRTUAL CAPITAL</div>
            <div class="metric-value">₹{acc['balance']:,.2f}</div>
            <div style="font-size: 0.75rem; color: #8B949E; margin-top: 4px;">Initial: ₹{acc['initial_capital']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with pcol2:
        pnl_val_c = "#00F5A0" if acc['realized_pnl'] >= 0 else "#FF3B69"
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">REALIZED NET P&L</div>
            <div class="metric-value" style="color: {pnl_val_c};">₹{acc['realized_pnl']:+,.2f}</div>
            <div style="font-size: 0.75rem; color: {pnl_val_c}; margin-top: 4px;">Return: {acc['return_pct']:+.2f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with pcol3:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">WIN PROBABILITY</div>
            <div class="metric-value" style="color: #00D2FF;">{win_rate}%</div>
            <div style="font-size: 0.75rem; color: #8B949E; margin-top: 4px;">Wins: {winning_trades} / {total_trades} Closed</div>
        </div>
        """, unsafe_allow_html=True)
    with pcol4:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">CAPITAL BUFFER</div>
            <div class="metric-value" style="color: #00F5A0;">₹{max(0, acc['balance'] - 65000):,.0f}</div>
            <div style="font-size: 0.75rem; color: #8B949E; margin-top: 4px;">Reserve for Adjustments</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

    st.markdown("#### ⚡ Active Open Multi-Leg Positions")
    open_pos = paper_eng.get_open_positions()
    if open_pos.empty:
        st.caption("No open positions. Deploy a strategy from Tab 2 to initiate trade monitoring.")
    else:
        for _, row in open_pos.iterrows():
            pts_diff = spot - row['entry_spot'] if 'Bullish' in row['strategy_type'] else row['entry_spot'] - spot
            mtm_pnl = pts_diff * row['lot_size'] * 0.4
            pnl_c = "#00F5A0" if mtm_pnl >= 0 else "#FF3B69"
            pcol1, pcol2, pcol3 = st.columns([3, 2, 1])
            with pcol1:
                st.markdown(f"**#{row['id']} {row['strategy_name']}** ({row['symbol']}) | Qty: `{row['lot_size']}`")
                st.caption(f"Entry: ₹{row['entry_spot']} | Net: ₹{row['net_credit_debit']}")
            with pcol2:
                st.markdown(f"<span class='mono' style='font-size: 1.15rem; font-weight: 800; color: {pnl_c};'>MTM PnL: ₹{mtm_pnl:+,.2f}</span>", unsafe_allow_html=True)
            with pcol3:
                if st.button("Square Off", key=f"sq_{row['id']}", use_container_width=True):
                    paper_eng.close_position(row['id'], spot, mtm_pnl, exit_reason="Manual Close")
                    st.rerun()

    st.divider()

    jhead_col1, jhead_col2 = st.columns([3, 1])
    with jhead_col1:
        st.markdown("#### 📓 Closed Trade Journal & Performance History")
    with jhead_col2:
        if st.button("🔄 Reset Portfolio (₹3,00,000 Capital)", key="reset_acc_btn", use_container_width=True):
            paper_eng.reset_account(300000.0)
            st.success("✅ Virtual Portfolio reset to ₹3,00,000 initial capital!")
            st.rerun()

    if jdf.empty:
        st.caption("No closed records in trade journal yet.")
    else:
        st.dataframe(jdf, hide_index=True, use_container_width=True)
        csv_data = jdf.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Trade Journal CSV",
            data=csv_data,
            file_name=f"trading_journal_{symbol}.csv",
            mime="text/csv"
        )

# -------------------------------------------------------------
# TAB 5: GEMINI QUANT COPILOT & VOICE
# -------------------------------------------------------------
with tabs[4]:
    thcol1, thcol2 = st.columns([4, 1])
    with thcol1:
        st.markdown("""
        <div>
            <div style="font-weight: 900; font-size: 1.3rem; color: #FFFFFF;">🤖 Gemini Flash (Prop-Desk Co-Pilot)</div>
            <div style="font-size: 0.85rem; color: #00D2FF;">Real-time Prop-Desk Masterclass aware AI Quant Partner in Hinglish</div>
        </div>
        """, unsafe_allow_html=True)
    with thcol2:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.gemini_messages = [
                {"role": "assistant", "content": "Namaste bhai! Chat memory fresh ho gayi hai. The Big Lizard, BWB, Long Calendars aur Margin & Funds Shield ke sath active hoon. Poocho!"}
            ]
            st.rerun()

    # Quick Action Prompt Chips
    st.markdown("<div style='font-size: 0.8rem; color: #8B949E; margin-bottom: 6px;'>⚡ Quick Prompts:</div>", unsafe_allow_html=True)
    qcol1, qcol2, qcol3, qcol4 = st.columns(4)
    
    quick_prompt = None
    with qcol1:
        if st.button("📅 Expiry Days Left Check", use_container_width=True):
            quick_prompt = f"Bhai {symbol} ki expiry kab hai aur expiry khatam hone me kitne din aur ghante bache hain?"
    with qcol2:
        if st.button("💼 Margin vs Funds Needed Check", use_container_width=True):
            quick_prompt = f"Bhai {symbol} par Margin Blocked vs Upfront Funds Needed aur Basket Execution Sequence ka rule samjhao."
    with qcol3:
        if st.button("🦎 Big Lizard Setup Samjhao", use_container_width=True):
            quick_prompt = f"Bhai {symbol} par The Big Lizard ka High-Yield ATM Call Spread aur Zero Upside Risk setup samjhao."
    with qcol4:
        if st.button("🛡️ 3-Level Defense Sentinel", use_container_width=True):
            quick_prompt = "Bhai Module 09 ke 3 Levels of Defense (Level 1 Roll, Level 2 Freeze Gamma, Level 3 Hard Exit) samjhao."

    st.divider()

    chat_container = st.container(height=380)
    with chat_container:
        for msg in st.session_state.gemini_messages:
            if msg["role"] == "user":
                st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-ai'><b>🤖 Gemini (Bhai):</b><br/>{msg['content']}</div>", unsafe_allow_html=True)

    user_input = st.chat_input("Bhai se Expiry days left, Margin, Funds Needed, ya adjustment ke baare mein kuch bhi pucho...")
    active_query = quick_prompt or user_input

    if active_query:
        st.session_state.gemini_messages.append({"role": "user", "content": active_query})
        
        with st.spinner("Gemini Flash live data analyze kar raha hai..."):
            ai_reply = GeminiLiveChat.query_gemini(
                active_query,
                market_context_dict,
                st.session_state.gemini_messages,
                api_key=config.get("GEMINI_API_KEY")
            )
        
        st.session_state.gemini_messages.append({"role": "assistant", "content": ai_reply})
        st.rerun()

    if st.session_state.gemini_messages and len(st.session_state.gemini_messages) > 1:
        latest_reply = st.session_state.gemini_messages[-1]["content"]
        if st.button("🔊 Suno: Latest Gemini Reply (Hindi Neural Voice)", key="play_latest_gemini_voice"):
            with st.spinner("Generating natural Hindi voice..."):
                audio_f = VoiceAICopilot.speak_text(latest_reply, "gemini_voice.mp3")
                if audio_f and os.path.exists(audio_f):
                    st.audio(audio_f, format="audio/mp3")

# -------------------------------------------------------------
# TAB 6: BROKER SETTINGS & PERSISTENT GATEWAY
# -------------------------------------------------------------
with tabs[5]:
    st.markdown("### ⚙️ Persistent Broker & API Gateway")
    bcol1, bcol2 = st.columns(2)
    
    with bcol1:
        st.markdown("""
        <div class="glass-card">
            <div style="font-weight: 800; font-size: 1.05rem; color: #FFFFFF; margin-bottom: 12px;">🔑 Fyers API v3 Credentials (Permanently Saved)</div>
        """, unsafe_allow_html=True)
        
        in_app_id = st.text_input("Fyers App ID (Client ID)", value=config.get("FYERS_APP_ID", ""))
        in_secret_id = st.text_input("Fyers Secret ID (Secret Key)", type="password", value=config.get("FYERS_SECRET_ID", ""))
        in_redirect_uri = st.text_input("Redirect URI", value=config.get("FYERS_REDIRECT_URI", "https://trade.fyers.in/api-login/"))
        in_token = st.text_input("Current Access Token", type="password", value=config.get("FYERS_ACCESS_TOKEN", ""))

        if st.button("💾 Save Fyers Credentials Permanently", key="save_fyers_btn"):
            ConfigManager.save_config({
                "FYERS_APP_ID": in_app_id,
                "FYERS_SECRET_ID": in_secret_id,
                "FYERS_REDIRECT_URI": in_redirect_uri,
                "FYERS_ACCESS_TOKEN": in_token
            })
            st.success("✅ Fyers credentials permanently saved to config.json and .env!")
            st.rerun()

        st.markdown("<hr style='border-color: rgba(255,255,255,0.06);'>", unsafe_allow_html=True)
        st.markdown("#### ⚡ 1-Click Daily Token Generator")
        st.caption("Subah market khulne se pehle sirf 1 baar Auth URL se token generate karein:")

        if in_app_id and in_secret_id:
            try:
                from fyers_apiv3 import fyersModel
                session_obj = fyersModel.SessionModel(
                    client_id=in_app_id,
                    secret_key=in_secret_id,
                    redirect_uri=in_redirect_uri,
                    response_type="code",
                    grant_type="authorization_code"
                )
                auth_link = session_obj.generate_authcode()
                st.markdown(f"""
                <div style="background: rgba(0, 210, 255, 0.1); border: 1px solid rgba(0, 210, 255, 0.3); padding: 10px; border-radius: 8px; margin-bottom: 10px;">
                    1. <a href="{auth_link}" target="_blank" style="color: #00F5A0; font-weight: bold; text-decoration: underline;">👉 Click Here: Fyers Login & Generate Auth Code</a><br/>
                    <small style="color: #8B949E;">Login karne ke baad browser ka pura redirected URL copy karein.</small>
                </div>
                """, unsafe_allow_html=True)

                redirected_url_input = st.text_input("2. Paste Redirected URL / Auth Code here:", placeholder="https://trade.fyers.in/api-login/?auth_code=...")
                if st.button("🔑 Generate & Save Access Token", key="gen_token_btn"):
                    if redirected_url_input:
                        match = re.search(r"auth_code=([^&]+)", redirected_url_input)
                        code_val = match.group(1) if match else redirected_url_input.strip()
                        session_obj.set_token(code_val)
                        res = session_obj.generate_token()
                        if "access_token" in res:
                            new_tok = res["access_token"]
                            ConfigManager.save_config({"FYERS_ACCESS_TOKEN": new_tok})
                            st.success("🎉 Access Token Generated & Saved Permanently! Fyers is 100% Connected!")
                            st.rerun()
                        else:
                            st.error(f"Failed to generate token: {res.get('message', 'Unknown Error')}")
                    else:
                        st.warning("Pehle upar diye gaye link se login karke redirected URL paste karo.")
            except Exception as e:
                st.error(f"Error setting up session: {e}")
        else:
            st.info("Pehle upar Fyers App ID aur Secret ID daal kar save karein.")

        st.markdown("</div>", unsafe_allow_html=True)

    with bcol2:
        st.markdown("""
        <div class="glass-card">
            <div style="font-weight: 800; font-size: 1.05rem; color: #00F5A0; margin-bottom: 10px;">🤖 Google Gemini Key (Permanently Saved)</div>
            <div style="font-size: 0.82rem; color: #8B949E; margin-bottom: 10px;">
                100% Free Gemini API Key: <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color: #00D2FF; font-weight: bold;">Google AI Studio</a>
            </div>
        """, unsafe_allow_html=True)
        gem_key_input = st.text_input("Gemini API Key", value=config.get("GEMINI_API_KEY", ""), type="password", placeholder="AQ.Ab8RN...")
        if st.button("💾 Save Gemini Key Permanently", key="save_gem_key"):
            ConfigManager.save_config({"GEMINI_API_KEY": gem_key_input})
            st.success("✅ Gemini API Key permanently saved to config.json and .env! AI Chat is active.")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
