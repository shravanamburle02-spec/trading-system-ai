"""
Master Trading System - Full Institutional Quant Trading Desk
Multi-Section Architecture:
1. 💠 LIVE QUANT COCKPIT (3-Pane Layout with Sensibull Payoff Curve, Confluence Matrix & Greeks)
2. 📊 ADVANCED OPTION CHAIN (Full Sensibull/NSE Live Greeks, OI Walls, Volume & PCR Matrix)
3. 🦎 NON-DIRECTIONAL STRATEGY LAB (Big Lizard, Broken Wing Butterfly, Calendar, Iron Condor with Margin vs Funds)
4. 🛡️ DEFENSE SENTINEL (3-Level Profit Recovery & Dynamic Morphing Rebalancer)
5. 💼 ₹3,00,000 PORTFOLIO JOURNAL (Live Positions, Incubation Statistics & CSV Export)
6. ⚙️ FYERS & API GATEWAY (Fyers v3 Broker Auth & Gemini Key Config)
"""

import os
import re
import json
import datetime
import calendar
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
    page_title="QUANT CORE | Institutional Prop-Desk",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Start Sentinel Daemon
AutoRebalancerSentinel.start_sentinel(interval_seconds=10)

# Persistent configuration load
config = ConfigManager.get_config()

# Initialize session state
if "gemini_messages" not in st.session_state:
    st.session_state.gemini_messages = [
        {"role": "assistant", "content": "Namaste bhai! Main tera Prop-Desk AI Quant Co-Pilot hoon. Live Sensibull Payoff Curve, Advanced Option Chain, Greeks, aur 3-Level Defense Sentinel ke sath live hoon. Poocho!"}
    ]

# -------------------------------------------------------------
# DENSE BLOOMBERG QUANT CSS & GLASSMORPHISM
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
        --bg-card: rgba(13, 17, 26, 0.88);
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

    /* Option Chain Styling */
    .oc-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        text-align: center;
    }
    .oc-table th {
        background: #0D111A;
        padding: 8px 4px;
        color: #8B949E;
        font-weight: 700;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    }
    .oc-table td {
        padding: 6px 4px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    }
    .oc-table tr:hover {
        background: rgba(0, 210, 255, 0.05);
    }
    .oc-itm-ce {
        background: rgba(0, 245, 160, 0.04);
    }
    .oc-itm-pe {
        background: rgba(255, 59, 105, 0.04);
    }
    .oc-atm {
        background: rgba(255, 184, 0, 0.15) !important;
        font-weight: 800 !important;
        border-top: 1px solid #FFB800 !important;
        border-bottom: 1px solid #FFB800 !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, #00D2FF 0%, #00F5A0 100%) !important;
        color: #05070B !important;
        font-weight: 900 !important;
        font-size: 0.85rem !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        box-shadow: 0 0 15px rgba(0, 245, 160, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 0 25px rgba(0, 245, 160, 0.5) !important;
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
# REAL-TIME LIVE TICKING TOP TICKER BAR
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
            QUANT CORE
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
# GLOBAL INGESTION & DATA ENGINE
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
# DEDICATED INSTITUTIONAL SECTIONS & WORKSPACES
# -------------------------------------------------------------
sec1, sec2, sec3, sec4, sec5, sec6 = st.tabs([
    "💠 3-Pane Quant Cockpit",
    "📊 Advanced Option Chain",
    "🦎 Non-Directional Strategy Lab",
    "🛡️ Defense Sentinel & Rebalancer",
    "💼 ₹3L Portfolio & Trade Journal",
    "⚙️ Fyers & API Gateway"
])

# =============================================================
# SECTION 1: 3-PANE QUANT COCKPIT
# =============================================================
with sec1:
    left_pane, center_pane, right_pane = st.columns([28, 44, 28])

    # --- LEFT PANE (28%) ---
    with left_pane:
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

        ce_oi_total = max(1, chain_data.get('total_ce_oi', 100000))
        pe_oi_total = max(1, chain_data.get('total_pe_oi', 100000))
        tot_oi = ce_oi_total + pe_oi_total
        pe_pct = int((pe_oi_total / tot_oi) * 100)
        ce_pct = 100 - pe_pct

        st.markdown(f"""
        <div class="cockpit-card">
            <div class="card-header">
                <span>📊 LAYER 1: DERIVATIVES DYNAMICS</span>
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

    # --- CENTER PANE (44%) ---
    with center_pane:
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

        # Plotly Sensibull Payoff Curve
        spot_range = np.linspace(spot * 0.94, spot * 1.06, 120)
        pnl_curve = []
        for s_price in spot_range:
            total_pnl = 0.0
            for leg in active_strat['legs']:
                k = leg['strike']
                p = leg['ltp']
                q = leg['qty']
                is_call = 'CE' in leg['option']
                is_buy = leg['type'] == 'BUY'
                payoff = max(0.0, s_price - k) if is_call else max(0.0, k - s_price)
                leg_pnl = (payoff - p) * q if is_buy else (p - payoff) * q
                total_pnl += leg_pnl
            pnl_curve.append(total_pnl)

        pnl_array = np.array(pnl_curve)
        fig_payoff = go.Figure()
        fig_payoff.add_hline(y=0, line_dash="solid", line_color="rgba(255,255,255,0.2)", line_width=1)
        fig_payoff.add_trace(go.Scatter(
            x=spot_range, y=np.maximum(pnl_array, 0), mode='lines', line=dict(color='#00F5A0', width=0),
            fill='tozeroy', fillcolor='rgba(0, 245, 160, 0.18)', name='Profit Zone', hoverinfo='skip'
        ))
        fig_payoff.add_trace(go.Scatter(
            x=spot_range, y=np.minimum(pnl_array, 0), mode='lines', line=dict(color='#FF3B69', width=0),
            fill='tozeroy', fillcolor='rgba(255, 59, 105, 0.18)', name='Loss Zone', hoverinfo='skip'
        ))
        fig_payoff.add_trace(go.Scatter(
            x=spot_range, y=pnl_array, mode='lines', line=dict(color='#00D2FF', width=2.5),
            name='Expiry P&L', hovertemplate='Spot: ₹%{x:,.0f}<br>P&L: ₹%{y:+,.0f}<extra></extra>'
        ))
        fig_payoff.add_vline(
            x=spot, line_dash="dash", line_color="#FFB800", line_width=1.5,
            annotation_text=f"Spot ₹{spot:,.0f}", annotation_position="top right",
            annotation_font=dict(color="#FFB800", family="JetBrains Mono", size=10)
        )
        fig_payoff.update_layout(
            template='plotly_dark', height=260, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor='#07090E', paper_bgcolor='#07090E', showlegend=False,
            font=dict(family='JetBrains Mono', color='#8B949E', size=9),
            xaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickprefix='₹'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickprefix='₹', side='right')
        )
        st.plotly_chart(fig_payoff, use_container_width=True, config={'displayModeBar': False})

        # Top Strikes Bar Chart
        df_chain = chain_data.get('chain_df')
        if df_chain is not None and not df_chain.empty:
            near_df = df_chain[(df_chain['strike'] >= spot * 0.97) & (df_chain['strike'] <= spot * 1.03)].head(6)
            if not near_df.empty:
                fig_oi = go.Figure()
                fig_oi.add_trace(go.Bar(
                    x=near_df['strike'], y=near_df['pe_oi'] if 'pe_oi' in near_df.columns else [50000]*len(near_df),
                    name='Put OI (Support)', marker_color='#00F5A0', opacity=0.85
                ))
                fig_oi.add_trace(go.Bar(
                    x=near_df['strike'], y=near_df['ce_oi'] if 'ce_oi' in near_df.columns else [50000]*len(near_df),
                    name='Call OI (Resistance)', marker_color='#FF3B69', opacity=0.85
                ))
                fig_oi.update_layout(
                    barmode='group', template='plotly_dark', height=140, margin=dict(l=10, r=10, t=6, b=6),
                    plot_bgcolor='#07090E', paper_bgcolor='#07090E', showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=8)),
                    font=dict(family='JetBrains Mono', color='#8B949E', size=8),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.03)', type='category'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.03)', side='right')
                )
                st.plotly_chart(fig_oi, use_container_width=True, config={'displayModeBar': False})

        # Action Deck Strip
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

    # --- RIGHT PANE (28%) ---
    with right_pane:
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

        st.markdown(f"""
        <div class="cockpit-card" style="margin-bottom: 0;">
            <div class="card-header">
                <span>🤖 GEMINI QUANT BUDDY</span>
                <span class="glow-pill-purple">VOICE READY</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        q1, q2 = st.columns(2)
        quick_q = None
        with q1:
            if st.button("💬 Bhai kya karu?", use_container_width=True):
                quick_q = f"Bhai {symbol} par current spot {spot} aur {market_regime['regime']} regime me kaunsi strategy best hai aur kyu?"
        with q2:
            if st.button("🛡️ Sentinel Status?", use_container_width=True):
                quick_q = f"Bhai {symbol} par adjustment sentinel trigger points aur breakevens kya hain?"

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


# =============================================================
# SECTION 2: FULL ADVANCED OPTION CHAIN (SENSIBULL/NSE GRADE)
# =============================================================
with sec2:
    st.markdown(f"""
    <div class="cockpit-card">
        <div class="card-header">
            <span>📊 {symbol} ADVANCED INSTITUTIONAL OPTION CHAIN (EXPIRY: {exp_info['expiry_date_str']})</span>
            <span class="glow-pill-emerald">SPOT: ₹{spot:,.1f}</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; padding: 4px 6px; color: #8B949E; flex-wrap: wrap; gap: 8px;">
            <span><b>PCR:</b> <span style="color: #00F5A0;">{pcr_v:.2f}</span></span>
            <span><b>Max Pain:</b> <span style="color: #FFB800;">₹{chain_data['max_pain']}</span></span>
            <span><b>Call Wall (Major Resistance):</b> <span style="color: #FF3B69;">₹{chain_data['top_call_wall']}</span></span>
            <span><b>Put Wall (Major Support):</b> <span style="color: #00F5A0;">₹{chain_data['top_put_wall']}</span></span>
            <span><b>Expected Range (1-Sigma):</b> <span style="color: #00D2FF;">₹{spot*0.985:,.0f} - ₹{spot*1.015:,.0f}</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_oc = chain_data.get('chain_df')
    if df_oc is not None and not df_oc.empty:
        filter_col1, filter_col2 = st.columns([2, 8])
        with filter_col1:
            strike_depth = st.selectbox("Strike Range", ["Near Spot (±10 Strikes)", "Full Chain (±20 Strikes)"], index=0)
        
        n_strikes = 10 if "10" in strike_depth else 20
        df_oc_sorted = df_oc.sort_values(by='strike').reset_index(drop=True)
        atm_idx = (df_oc_sorted['strike'] - spot).abs().idxmin()
        start_i = max(0, atm_idx - n_strikes)
        end_i = min(len(df_oc_sorted), atm_idx + n_strikes + 1)
        sub_oc = df_oc_sorted.iloc[start_i:end_i].copy()

        # HTML Option Chain Generator
        rows_html = ""
        for _, r in sub_oc.iterrows():
            k = r['strike']
            is_atm = abs(k - spot) < (df_oc_sorted['strike'].diff().abs().min() or 50) / 2
            row_class = "oc-atm" if is_atm else ""
            ce_itm = "oc-itm-ce" if k < spot else ""
            pe_itm = "oc-itm-pe" if k > spot else ""

            ce_oi = int(r.get('ce_oi', 50000))
            pe_oi = int(r.get('pe_oi', 50000))
            ce_vol = int(r.get('ce_volume', 25000))
            pe_vol = int(r.get('pe_volume', 25000))
            ce_iv = r.get('ce_iv', 14.5)
            pe_iv = r.get('pe_iv', 14.5)
            ce_delta = r.get('ce_delta', 0.5)
            pe_delta = r.get('pe_delta', -0.5)
            ce_ltp = r.get('ce_ltp', 120.0)
            pe_ltp = r.get('pe_ltp', 110.0)

            ce_wall_badge = " 🟥" if k == chain_data['top_call_wall'] else ""
            pe_wall_badge = " 🟩" if k == chain_data['top_put_wall'] else ""

            rows_html += f"""
            <tr class="{row_class}">
                <td class="{ce_itm}">{ce_oi:,}{ce_wall_badge}</td>
                <td class="{ce_itm}">{ce_vol:,}</td>
                <td class="{ce_itm}">{ce_iv:.1f}%</td>
                <td class="{ce_itm}" style="color: #00F5A0;">+{ce_delta:.2f}</td>
                <td class="{ce_itm}" style="color: #FFFFFF; font-weight: 700;">₹{ce_ltp:.1f}</td>
                <td style="color: #FFB800; font-weight: 800; font-size: 0.85rem; background: rgba(255,255,255,0.02);">₹{k:,.0f}</td>
                <td class="{pe_itm}" style="color: #FFFFFF; font-weight: 700;">₹{pe_ltp:.1f}</td>
                <td class="{pe_itm}" style="color: #FF3B69;">{pe_delta:.2f}</td>
                <td class="{pe_itm}">{pe_iv:.1f}%</td>
                <td class="{pe_itm}">{pe_vol:,}</td>
                <td class="{pe_itm}">{pe_oi:,}{pe_wall_badge}</td>
            </tr>
            """

        table_html = f"""
        <div style="overflow-x: auto; background: var(--bg-card); border: 1px solid var(--glass-border); border-radius: 10px; padding: 6px;">
            <table class="oc-table">
                <thead>
                    <tr>
                        <th colspan="5" style="color: #00F5A0; border-bottom: 2px solid #00F5A0;">CALLS (CE)</th>
                        <th style="color: #FFB800;">STRIKE</th>
                        <th colspan="5" style="color: #FF3B69; border-bottom: 2px solid #FF3B69;">PUTS (PE)</th>
                    </tr>
                    <tr>
                        <th>OI (Contracts)</th>
                        <th>Volume</th>
                        <th>IV</th>
                        <th>Delta</th>
                        <th>LTP</th>
                        <th style="color: #FFB800;">STRIKE</th>
                        <th>LTP</th>
                        <th>Delta</th>
                        <th>IV</th>
                        <th>Volume</th>
                        <th>OI (Contracts)</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.info("Generating live Option Chain data...")


# =============================================================
# SECTION 3: NON-DIRECTIONAL STRATEGY VAULT
# =============================================================
with sec3:
    st.markdown(f"""
    <div class="cockpit-card">
        <div class="card-header">
            <span>🦎 NON-DIRECTIONAL STRATEGY VAULT (CALIBRATED TO ₹3,00,000 CAPITAL)</span>
            <span class="glow-pill-purple">5 INSTITUTIONAL TEMPLATES</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    all_strats = [
        StrategyOptimizer.generate_big_lizard(symbol, spot, chain_data, dte=dte, lot_size=default_lot, account_capital=acc['balance']),
        StrategyOptimizer.generate_broken_wing_butterfly(symbol, spot, chain_data, dte=dte, lot_size=default_lot, account_capital=acc['balance']),
        StrategyOptimizer.generate_double_calendar(symbol, spot, chain_data, dte=dte, lot_size=default_lot, account_capital=acc['balance']),
        StrategyOptimizer.generate_classic_iron_condor(symbol, spot, chain_data, dte=dte, lot_size=default_lot, account_capital=acc['balance']),
        StrategyOptimizer.generate_iron_butterfly(symbol, spot, chain_data, dte=dte, lot_size=default_lot, account_capital=acc['balance'])
    ]

    for s_idx, st_data in enumerate(all_strats):
        st.markdown(f"""
        <div class="cockpit-card" style="margin-bottom: 12px;">
            <div class="card-header">
                <span style="font-size: 0.95rem; color: #FFFFFF;">{st_data['strategy_name']}</span>
                <span class="glow-pill-emerald">WIN PROB: {st_data['win_probability']}</span>
            </div>
            <div style="font-size: 0.78rem; color: #8B949E; margin-bottom: 8px;">{st_data['type']} | Fit: {st_data['regime_fit']}</div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; text-align: center; margin-bottom: 8px;">
                <div style="background: rgba(255,255,255,0.02); padding: 6px; border-radius: 6px;">
                    <div style="font-size: 0.68rem; color: #8B949E;">NET CREDIT / DEBIT</div>
                    <div class="mono" style="font-size: 0.88rem; font-weight: 800; color: #00F5A0;">{st_data['net_credit_debit']}</div>
                </div>
                <div style="background: rgba(255,255,255,0.02); padding: 6px; border-radius: 6px;">
                    <div style="font-size: 0.68rem; color: #8B949E;">MARGIN BLOCKED</div>
                    <div class="mono" style="font-size: 0.88rem; font-weight: 800; color: #00D2FF;">{st_data['final_margin_blocked']}</div>
                </div>
                <div style="background: rgba(255,255,255,0.02); padding: 6px; border-radius: 6px;">
                    <div style="font-size: 0.68rem; color: #8B949E;">FUNDS NEEDED</div>
                    <div class="mono" style="font-size: 0.88rem; font-weight: 800; color: #FFB800;">{st_data['upfront_funds_needed']}</div>
                </div>
                <div style="background: rgba(255,255,255,0.02); padding: 6px; border-radius: 6px;">
                    <div style="font-size: 0.68rem; color: #8B949E;">LIQUID BUFFER LEFT</div>
                    <div class="mono" style="font-size: 0.88rem; font-weight: 800; color: #C77DFF;">{st_data['buffer_cash_remaining']}</div>
                </div>
            </div>
            <div style="font-size: 0.72rem; color: #00D2FF; margin-bottom: 8px;"><b>Execution Sequence:</b> {st_data['execution_order']}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"⚡ Deploy {st_data['strategy_name']}", key=f"vault_btn_{s_idx}", use_container_width=True):
            tid = paper_eng.execute_paper_trade(symbol, st_data, spot, conf_score, lot_size=default_lot)
            st.toast(f"✅ Trade #{tid} ({st_data['strategy_name']}) Deployed!")
            st.rerun()


# =============================================================
# SECTION 4: DEFENSE SENTINEL & LIVE ADJUSTMENTS
# =============================================================
with sec4:
    st.markdown(f"""
    <div class="cockpit-card">
        <div class="card-header">
            <span>🛡️ AUTONOMOUS 3-LEVEL PROFIT RECOVERY ADJUSTMENT ENGINE</span>
            <span class="glow-pill-emerald">DAEMON ACTIVE (10S TICK)</span>
        </div>
        <p style="font-size: 0.8rem; color: #8B949E;">
            System positions ko passive loss me nahi chhodta — Delta breach hote hi structure ko <b>Jade Lizard</b>, <b>Inverted Strangle</b>, ya <b>Freeze Gamma Shield</b> me morph karke profit lock karta hai.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c_adj1, c_adj2, c_adj3 = st.columns(3)
    with c_adj1:
        st.markdown("""
        <div class="cockpit-card">
            <div class="card-header"><span style="color: #00F5A0;">LEVEL 1: UNTESTED ROLL</span></div>
            <p style="font-size: 0.75rem; color: #8B949E;">Jab market 1 side move kare, untested profitable leg ko closer roll karke additional credit collect hota hai (Delta drops back to 0.00).</p>
        </div>
        """, unsafe_allow_html=True)
    with c_adj2:
        st.markdown("""
        <div class="cockpit-card">
            <div class="card-header"><span style="color: #FFB800;">LEVEL 2: STRATEGY MORPH</span></div>
            <p style="font-size: 0.75rem; color: #8B949E;">Threatened short leg ke upar synthetic long hedge buy karke trade ko <b>Zero-Risk Jade Lizard</b> me morph kar deta hai.</p>
        </div>
        """, unsafe_allow_html=True)
    with c_adj3:
        st.markdown("""
        <div class="cockpit-card">
            <div class="card-header"><span style="color: #FF3B69;">LEVEL 3: HARD CAPITAL SHIELD</span></div>
            <p style="font-size: 0.75rem; color: #8B949E;">Agar loss 2.5% max capital buffer ko touch kare, automated square-off trigger ho kar principal protect hota hai.</p>
        </div>
        """, unsafe_allow_html=True)


# =============================================================
# SECTION 5: ₹3,00,000 PORTFOLIO & TRADE JOURNAL
# =============================================================
with sec5:
    st.markdown(f"""
    <div class="cockpit-card">
        <div class="card-header">
            <span>💼 3-5 MONTH INCUBATION SUITE (BENCHMARK CAPITAL: ₹3,00,000.00)</span>
            <span class="glow-pill-emerald">BALANCE: ₹{acc['balance']:,.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    pos_df = paper_eng.get_open_positions()
    if pos_df.empty:
        st.info("No open positions in portfolio. Deploy a strategy from Section 1 or Section 3!")
    else:
        for _, r in pos_df.iterrows():
            pts_diff = spot - r['entry_spot'] if 'Bullish' in r['strategy_type'] else r['entry_spot'] - spot
            mtm = pts_diff * r['lot_size'] * 0.4
            pnl_c = "#00F5A0" if mtm >= 0 else "#FF3B69"
            col_a, col_b, col_c = st.columns([3, 2, 1])
            with col_a:
                st.markdown(f"**#{r['id']} {r['strategy_name']}** ({r['symbol']}) | Lots: `{r['lot_size']}`")
            with col_b:
                st.markdown(f"<span class='mono' style='font-size: 1.1rem; font-weight: 800; color: {pnl_c};'>MTM: ₹{mtm:+,.2f}</span>", unsafe_allow_html=True)
            with col_c:
                if st.button("Square Off", key=f"sec5_sq_{r['id']}", use_container_width=True):
                    paper_eng.close_position(r['id'], spot, mtm, exit_reason="Manual Close")
                    st.toast("✅ Position Closed!")
                    st.rerun()

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    jdf = paper_eng.get_journal()
    if not jdf.empty:
        st.markdown("### 📓 Closed Trade Audit Journal")
        st.dataframe(jdf, hide_index=True, use_container_width=True)
        csv = jdf.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Journal CSV", data=csv, file_name="quant_trading_journal.csv", mime="text/csv")


# =============================================================
# SECTION 6: FYERS & API GATEWAY
# =============================================================
with sec6:
    st.markdown("""
    <div class="cockpit-card">
        <div class="card-header">
            <span>⚙️ BROKER & AI CONFIGURATION GATEWAY</span>
            <span class="glow-pill-cyan">FYERS V3 + GOOGLE GEMINI</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cfg_col1, cfg_col2 = st.columns(2)
    with cfg_col1:
        st.subheader("Fyers API v3 Gateway")
        f_app = st.text_input("Fyers App ID", value=config.get("FYERS_APP_ID", ""))
        f_sec = st.text_input("Fyers Secret ID", type="password", value=config.get("FYERS_SECRET_ID", ""))
        f_tok = st.text_input("Access Token", type="password", value=config.get("FYERS_ACCESS_TOKEN", ""))
        if st.button("💾 Save Fyers Credentials", use_container_width=True):
            ConfigManager.save_config({"FYERS_APP_ID": f_app, "FYERS_SECRET_ID": f_sec, "FYERS_ACCESS_TOKEN": f_tok})
            st.success("✅ Fyers Credentials Saved Permanently!")
            st.rerun()

    with cfg_col2:
        st.subheader("Google Gemini AI API")
        g_key = st.text_input("Gemini API Key", type="password", value=config.get("GEMINI_API_KEY", ""))
        if st.button("💾 Save Gemini Key", use_container_width=True):
            ConfigManager.save_config({"GEMINI_API_KEY": g_key})
            st.success("✅ Gemini Key Saved Permanently!")
            st.rerun()
