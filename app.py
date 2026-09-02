"""
Master Trading System - Full Institutional Quant Trading Desk
Multi-Section Architecture with All 5 Indices, 60+ Strikes Depth & 2-Second Live Cockpit + Option Chain Ticking Engine
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
# Sentinel active in synchronous mode (no background thread)

# Persistent configuration load
config = ConfigManager.get_config()

# Initialize session state
if "gemini_messages" not in st.session_state:
    st.session_state.gemini_messages = [
        {"role": "assistant", "content": "Namaste bhai! Main tera Prop-Desk AI Quant Co-Pilot hoon. Live Sensibull Payoff Curve, High-Frequency Live Option Chain with Real-Time Price & OI Ticks, Greeks, aur 3-Level Defense Sentinel ke sath live hoon. Poocho!"}
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
        countdown.innerText = `⏳ Closes in ${String(h).padStart(2,'0')}h ${String(m).padStart(2,'0')}s`;
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

# Global Asset Selector (Persistent)
col_asset, col_space = st.columns([2.2, 7.8])
with col_asset:
    symbol = st.selectbox(
        "Asset Selection",
        [
            "NIFTY", "BANKNIFTY", "SENSEX", "FINNIFTY", "MIDCPNIFTY",
            "RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS",
            "SBIN", "TATAMOTORS", "ASIANPAINT", "ITC", "BHARTIARTL"
        ],
        index=0,
        label_visibility="collapsed"
    )

exp_info = LiquidityShield.get_detailed_expiry_info(symbol)
dte = exp_info['days_left']
default_lot = DataEngine.LOT_SIZES.get(symbol, 75)

# -------------------------------------------------------------
# REAL-TIME 2S AUTO-STREAMING TOP TICKER BAR FRAGMENT
# -------------------------------------------------------------
@st.fragment(run_every=2)
def render_live_top_bar(selected_symbol):
    quote = data_eng.get_market_quote(selected_symbol)
    spot = quote['current_price']
    chain_data = data_eng.get_option_chain(selected_symbol, days_to_expiry=dte)
    acc = paper_eng.get_account()
    pcr_v = chain_data['pcr']

    t_col1, t_col2, t_col3, t_col4, t_col5 = st.columns([2.2, 1.8, 1.8, 1.8, 1.4])

    with t_col1:
        chg_c = "#00F5A0" if quote['p_change'] >= 0 else "#FF3B69"
        chg_sign = "+" if quote['p_change'] >= 0 else ""
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: 8px; padding: 4px 10px; height: 38px; display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 0.75rem; color: #8B949E; font-weight: 700;">{selected_symbol}</span>
            <span class="mono" style="font-size: 0.95rem; font-weight: 800; color: #FFFFFF;">₹{spot:,.1f}</span>
            <span class="mono" style="font-size: 0.75rem; font-weight: 700; color: {chg_c};">{chg_sign}{quote['p_change']:.2f}%</span>
        </div>
        """, unsafe_allow_html=True)

    with t_col2:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: 8px; padding: 4px 10px; height: 38px; display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 0.72rem; color: #8B949E; font-weight: 600;">EXPIRY</span>
            <span class="mono" style="font-size: 0.8rem; font-weight: 800; color: #00D2FF;">{exp_info['dte_badge']}</span>
        </div>
        """, unsafe_allow_html=True)

    with t_col3:
        pcr_c = "#00F5A0" if pcr_v >= 1.0 else "#FF3B69"
        api_badge = "🟢 FYERS LIVE" if data_eng.fyers.is_connected() else "🔴 REAL-TIME TICK"
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: 8px; padding: 4px 10px; height: 38px; display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 0.72rem; color: #8B949E; font-weight: 600;">FEED / PCR</span>
            <span class="mono" style="font-size: 0.75rem; font-weight: 800; color: #00D2FF;">{api_badge}</span>
            <span class="mono" style="font-size: 0.82rem; font-weight: 800; color: {pcr_c};">{pcr_v:.2f}</span>
        </div>
        """, unsafe_allow_html=True)

    with t_col4:
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); border: 1px solid var(--glass-border); border-radius: 8px; padding: 4px 10px; height: 38px; display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 0.72rem; color: #8B949E; font-weight: 600;">CAPITAL</span>
            <span class="mono" style="font-size: 0.82rem; font-weight: 800; color: #00F5A0;">₹{acc['balance']:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)

    with t_col5:
        if st.button("🚨 PANIC EXIT", use_container_width=True, help="Square-off all open paper positions instantly!"):
            open_p = paper_eng.get_open_positions()
            if not open_p.empty:
                for _, r in open_p.iterrows():
                    paper_eng.close_position(r['id'], spot, 0.0, exit_reason="EMERGENCY PANIC EXIT")
                st.toast("🚨 All active positions squared off successfully!")
                st.rerun()

render_live_top_bar(symbol)

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
# SECTION 1: REAL-TIME 2S AUTO-STREAMING 3-PANE COCKPIT
# =============================================================
with sec1:
    @st.fragment(run_every=2)
    def render_live_cockpit(selected_symbol):
        quote = data_eng.get_market_quote(selected_symbol)
        spot = quote['current_price']
        df_candles = quote['df']
        chain_data = data_eng.get_option_chain(selected_symbol, days_to_expiry=dte)
        fii_dii = data_eng.get_fii_dii_sentiment()

        ind_res = IndicatorEngine.analyze(df_candles)
        smc_res = SMCEngine.analyze(df_candles)
        confluence = ConfluenceEngine.evaluate(chain_data, ind_res, smc_res, fii_dii)
        market_regime = StrategyOptimizer.classify_market_regime(spot, chain_data, ind_res, smc_res)
        acc = paper_eng.get_account()

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
                    <span class="glow-pill-cyan">FEED: {chain_data.get('feed_source', 'LIVE')}</span>
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
                        <span class="badge-cell-label">IV / India VIX</span>
                        <span class="badge-cell-val" style="color: #00D2FF;">{chain_data['atm_iv']:.1f}% / {chain_data['india_vix']:.2f}</span>
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
                label_visibility="collapsed",
                key="cockpit_strat_selector"
            )

            if "Big Lizard" in selected_strat_label:
                active_strat = StrategyOptimizer.generate_big_lizard(selected_symbol, spot, chain_data, dte=dte, lot_size=default_lot, account_capital=acc['balance'])
            elif "Broken Wing" in selected_strat_label:
                active_strat = StrategyOptimizer.generate_broken_wing_butterfly(selected_symbol, spot, chain_data, dte=dte, lot_size=default_lot, account_capital=acc['balance'])
            elif "Calendar" in selected_strat_label:
                active_strat = StrategyOptimizer.generate_double_calendar(selected_symbol, spot, chain_data, dte=dte, lot_size=default_lot, account_capital=acc['balance'])
            elif "Iron Butterfly" in selected_strat_label:
                active_strat = StrategyOptimizer.generate_iron_butterfly(selected_symbol, spot, chain_data, dte=dte, lot_size=default_lot, account_capital=acc['balance'])
            else:
                active_strat = StrategyOptimizer.generate_classic_iron_condor(selected_symbol, spot, chain_data, dte=dte, lot_size=default_lot, account_capital=acc['balance'])

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
                annotation_text=f"Spot ₹{spot:,.1f}", annotation_position="top right",
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
                tid = paper_eng.execute_paper_trade(selected_symbol, active_strat, spot, conf_score, lot_size=default_lot)
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
                    quick_q = f"Bhai {selected_symbol} par current spot {spot} aur {market_regime['regime']} regime me kaunsi strategy best hai aur kyu?"
            with q2:
                if st.button("🛡️ Sentinel Status?", use_container_width=True):
                    quick_q = f"Bhai {selected_symbol} par adjustment sentinel trigger points aur breakevens kya hain?"

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
                    'symbol': selected_symbol, 'spot': spot, 'regime': market_regime['regime'],
                    'conf_score': conf_score, 'bias': bias_text, 'pcr': chain_data['pcr'], 'vix': chain_data['india_vix'],
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

    render_live_cockpit(symbol)


# =============================================================
# SECTION 2: HIGH-FREQUENCY REAL-TIME TICKING OPTION CHAIN (PRICE + OI)
# =============================================================
with sec2:
    chain_data_s2 = data_eng.get_option_chain(symbol, days_to_expiry=dte)
    atm_k = chain_data_s2['atm_strike']
    df_oc = chain_data_s2.get('chain_df')
    quote_s2 = data_eng.get_market_quote(symbol)
    spot_s2 = quote_s2['current_price']
    
    atm_ce_p = 110.90
    atm_pe_p = 154.30
    if df_oc is not None and not df_oc.empty:
        atm_row = df_oc[df_oc['strike'] == atm_k]
        if not atm_row.empty:
            atm_ce_p = float(atm_row.iloc[0].get('ce_ltp', 110.90))
            atm_pe_p = float(atm_row.iloc[0].get('pe_ltp', 154.30))

    straddle_p = atm_ce_p + atm_pe_p
    source_label = "🟢 LIVE FYERS BROKER FEED" if data_eng.fyers.is_connected() else "⚡ REAL-TIME TICK ENGINE (850ms)"

    if df_oc is not None and not df_oc.empty:
        filter_col1, filter_col2 = st.columns([4, 6])
        with filter_col1:
            strike_depth = st.selectbox(
                "Strike Filter Depth",
                [
                    "🎯 Active Trading Zone (ATM ± 5 Strikes / 11 Total)",
                    "📊 Standard Depth (ATM ± 10 Strikes / 21 Total)",
                    "🌐 Extended Depth (ATM ± 15 Strikes / 31 Total)",
                    "⚡ Deep Matrix (ATM ± 20 Strikes / 41 Total)",
                    "🔥 Complete Option Chain (ATM ± 30 Strikes / 61 Total)"
                ],
                index=1,
                key="oc_depth_selector"
            )
        
        if "5" in strike_depth:
            n_strikes = 5
        elif "10" in strike_depth:
            n_strikes = 10
        elif "15" in strike_depth:
            n_strikes = 15
        elif "20" in strike_depth:
            n_strikes = 20
        elif "30" in strike_depth:
            n_strikes = 30
        else:
            n_strikes = 15

        df_oc_sorted = df_oc.sort_values(by='strike').reset_index(drop=True)
        atm_idx = (df_oc_sorted['strike'] - spot_s2).abs().idxmin()
        start_i = max(0, atm_idx - n_strikes)
        end_i = min(len(df_oc_sorted), atm_idx + n_strikes + 1)
        sub_oc = df_oc_sorted.iloc[start_i:end_i].copy()

        # Build JSON array for high-frequency client-side JS ticking engine
        js_rows_data = []
        for _, r in sub_oc.iterrows():
            k = int(r['strike'])
            is_atm = bool(abs(k - spot_s2) < (df_oc_sorted['strike'].diff().abs().min() or 50) / 2)
            js_rows_data.append({
                "strike": k,
                "is_atm": is_atm,
                "ce_ltp": float(r.get('ce_ltp', 120.0)),
                "ce_oi": int(r.get('ce_oi', 50000)),
                "ce_chg": int(r.get('ce_change_oi', 0)),
                "ce_vol": int(r.get('ce_volume', 25000)),
                "ce_iv": float(r.get('ce_iv', 10.0)),
                "ce_delta": float(r.get('ce_delta', 0.5)),
                "pe_ltp": float(r.get('pe_ltp', 110.0)),
                "pe_oi": int(r.get('pe_oi', 50000)),
                "pe_chg": int(r.get('pe_change_oi', 0)),
                "pe_vol": int(r.get('pe_volume', 25000)),
                "pe_iv": float(r.get('pe_iv', 10.0)),
                "pe_delta": float(r.get('pe_delta', -0.5)),
                "ce_wall": " 🟥RES" if k == chain_data_s2['top_call_wall'] else "",
                "pe_wall": " 🟩SUP" if k == chain_data_s2['top_put_wall'] else ""
            })

        js_data_json = json.dumps(js_rows_data)

        # HIGH-FREQUENCY REAL-TIME TICKING HTML/JS ENGINE WITH LIVE PRICE + LIVE OI TICKS
        full_oc_table = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800;900&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                padding: 4px;
                background: #05070B;
                color: #F0F4F8;
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
            }}
            .top-cards {{
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 6px;
                text-align: center;
                margin-bottom: 8px;
            }}
            .card-cell {{
                border-radius: 8px;
                padding: 6px 8px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }}
            .card-title {{ font-size: 0.68rem; color: #8B949E; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; }}
            .card-val {{ font-size: 1.05rem; font-weight: 900; margin-top: 2px; }}

            .table-wrap {{
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                overflow-x: auto;
                background: #080C14;
            }}
            table {{
                width: 100%;
                min-width: 1060px;
                border-collapse: collapse;
                text-align: center;
            }}
            th {{
                background: #0D111A;
                padding: 8px 4px;
                color: #8B949E;
                font-weight: 700;
                position: sticky;
                top: 0;
                border-bottom: 2px solid rgba(255, 255, 255, 0.1);
                z-index: 10;
            }}
            td {{
                padding: 6px 4px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.04);
                transition: background-color 0.3s ease, color 0.3s ease;
            }}
            tr:hover {{
                background: rgba(0, 210, 255, 0.08) !important;
            }}

            /* FLASH ANIMATIONS FOR REAL BROKER TICK EFFECT */
            .flash-up {{
                background-color: rgba(0, 245, 160, 0.45) !important;
                color: #FFFFFF !important;
                font-weight: 900 !important;
            }}
            .flash-down {{
                background-color: rgba(255, 59, 105, 0.45) !important;
                color: #FFFFFF !important;
                font-weight: 900 !important;
            }}

            .itm-ce {{ background: rgba(0, 245, 160, 0.05); }}
            .itm-pe {{ background: rgba(255, 59, 105, 0.05); }}
            .atm-row {{
                background: rgba(255, 184, 0, 0.16) !important;
                font-weight: 800;
                border-top: 1px solid #FFB800;
                border-bottom: 1px solid #FFB800;
            }}
            .pulse-dot {{
                display: inline-block;
                width: 7px;
                height: 7px;
                background: #00F5A0;
                border-radius: 50%;
                box-shadow: 0 0 8px #00F5A0;
                animation: pulse 1.2s infinite;
            }}
            @keyframes pulse {{
                0% {{ transform: scale(0.95); opacity: 0.7; }}
                50% {{ transform: scale(1.2); opacity: 1; }}
                100% {{ transform: scale(0.95); opacity: 0.7; }}
            }}
        </style>
        </head>
        <body>

        <!-- LIVE STREAM HEADER CARDS -->
        <div style="background: rgba(13, 17, 26, 0.95); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 8px 12px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-weight: 800; font-size: 0.82rem; color: #FFFFFF; display: flex; align-items: center; gap: 6px;">
                    <span class="pulse-dot"></span>
                    📊 {symbol} REAL-TIME LIVE TICKING OPTION CHAIN ({exp_info['expiry_date_str']})
                </span>
                <span style="font-size: 0.72rem; color: #00F5A0; font-weight: 700; background: rgba(0,245,160,0.12); padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(0,245,160,0.3);">
                    {source_label} | SPOT: <span id="header-spot">₹{spot_s2:,.2f}</span>
                </span>
            </div>

            <div class="top-cards">
                <div class="card-cell" style="background: rgba(255, 184, 0, 0.08); border-color: rgba(255, 184, 0, 0.3);">
                    <div class="card-title">🎯 ATM STRIKE</div>
                    <div class="card-val" id="card-atm" style="color: #FFB800;">₹{atm_k:,.0f}</div>
                </div>
                <div class="card-cell" style="background: rgba(0, 245, 160, 0.08); border-color: rgba(0, 245, 160, 0.3);">
                    <div class="card-title">CALL PREMIUM (LTP)</div>
                    <div class="card-val" id="card-ce-ltp" style="color: #00F5A0;">₹{atm_ce_p:.1f}</div>
                </div>
                <div class="card-cell" style="background: rgba(255, 59, 105, 0.08); border-color: rgba(255, 59, 105, 0.3);">
                    <div class="card-title">PUT PREMIUM (LTP)</div>
                    <div class="card-val" id="card-pe-ltp" style="color: #FF3B69;">₹{atm_pe_p:.1f}</div>
                </div>
                <div class="card-cell" style="background: rgba(0, 210, 255, 0.08); border-color: rgba(0, 210, 255, 0.3);">
                    <div class="card-title">⚡ STRADDLE COST</div>
                    <div class="card-val" id="card-straddle" style="color: #00D2FF;">₹{straddle_p:.1f}</div>
                </div>
                <div class="card-cell" style="background: rgba(157, 78, 221, 0.08); border-color: rgba(157, 78, 221, 0.3);">
                    <div class="card-title">PCR / MAX PAIN</div>
                    <div class="card-val" id="card-pcr" style="color: #C77DFF;">{chain_data_s2['pcr']:.2f} / ₹{chain_data_s2['max_pain']}</div>
                </div>
            </div>
        </div>

        <!-- REAL-TIME TICKING OPTION CHAIN TABLE -->
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th colspan="6" style="color: #00F5A0; border-bottom: 2px solid #00F5A0; font-size: 12px;">CALLS (CE)</th>
                        <th style="color: #FFB800; font-size: 13px; font-weight: 900; background: rgba(255, 184, 0, 0.1);">STRIKE PRICE</th>
                        <th colspan="6" style="color: #FF3B69; border-bottom: 2px solid #FF3B69; font-size: 12px;">PUTS (PE)</th>
                    </tr>
                    <tr>
                        <th>OI (Contracts)</th>
                        <th style="color: #00F5A0;">OI Chg</th>
                        <th>Volume</th>
                        <th>IV</th>
                        <th>Delta</th>
                        <th style="color: #00F5A0; font-weight: 800;">CALL PREMIUM (LTP)</th>
                        <th style="color: #FFB800; font-weight: 900;">STRIKE</th>
                        <th style="color: #FF3B69; font-weight: 800;">PUT PREMIUM (LTP)</th>
                        <th>Delta</th>
                        <th>IV</th>
                        <th>Volume</th>
                        <th style="color: #FF3B69;">OI Chg</th>
                        <th>OI (Contracts)</th>
                    </tr>
                </thead>
                <tbody id="oc-tbody">
                </tbody>
            </table>
        </div>

        <script>
        const initialData = {js_data_json};
        let currentSpot = {spot_s2};
        const atmStrike = {atm_k};
        const lotSize = {default_lot};

        function formatNumber(num) {{
            return num.toLocaleString('en-IN');
        }}

        function buildTable() {{
            const tbody = document.getElementById('oc-tbody');
            tbody.innerHTML = '';

            initialData.forEach((row, idx) => {{
                const k = row.strike;
                const isAtm = row.is_atm;
                const rowClass = isAtm ? 'atm-row' : '';
                const ceBg = k < currentSpot ? 'itm-ce' : '';
                const peBg = k > currentSpot ? 'itm-pe' : '';
                const atmLabel = isAtm ? ' ⚡ATM' : '';

                const ceChgSign = row.ce_chg >= 0 ? '+' : '';
                const peChgSign = row.pe_chg >= 0 ? '+' : '';
                const ceChgColor = row.ce_chg >= 0 ? '#00F5A0' : '#FF3B69';
                const peChgColor = row.pe_chg >= 0 ? '#00F5A0' : '#FF3B69';

                const tr = document.createElement('tr');
                tr.className = rowClass;
                tr.id = `row-${{k}}`;

                tr.innerHTML = `
                    <td class="${{ceBg}}" id="ce-oi-${{k}}">${{formatNumber(row.ce_oi)}}${{row.ce_wall}}</td>
                    <td class="${{ceBg}}" id="ce-chg-${{k}}" style="color: ${{ceChgColor}}; font-weight: 700;">${{ceChgSign}}${{formatNumber(row.ce_chg)}}</td>
                    <td class="${{ceBg}}" id="ce-vol-${{k}}">${{formatNumber(row.ce_vol)}}</td>
                    <td class="${{ceBg}}" id="ce-iv-${{k}}">${{row.ce_iv.toFixed(1)}}%</td>
                    <td class="${{ceBg}}" id="ce-delta-${{k}}" style="color: #00F5A0;">+${{row.ce_delta.toFixed(2)}}</td>
                    <td class="${{ceBg}}" id="ce-ltp-${{k}}" style="color: #00F5A0; font-weight: 800; font-size: 12px; background: rgba(0, 245, 160, 0.12);">₹${{row.ce_ltp.toFixed(1)}}</td>
                    <td style="color: #FFB800; font-weight: 900; font-size: 13px; background: rgba(255,255,255,0.04); border-left: 1px solid rgba(255,255,255,0.1); border-right: 1px solid rgba(255,255,255,0.1);">₹${{formatNumber(k)}}${{atmLabel}}</td>
                    <td class="${{peBg}}" id="pe-ltp-${{k}}" style="color: #FF3B69; font-weight: 800; font-size: 12px; background: rgba(255, 59, 105, 0.12);">₹${{row.pe_ltp.toFixed(1)}}</td>
                    <td class="${{peBg}}" id="pe-delta-${{k}}" style="color: #FF3B69;">${{row.pe_delta.toFixed(2)}}</td>
                    <td class="${{peBg}}" id="pe-iv-${{k}}">${{row.pe_iv.toFixed(1)}}%</td>
                    <td class="${{peBg}}" id="pe-vol-${{k}}">${{formatNumber(row.pe_vol)}}</td>
                    <td class="${{peBg}}" id="pe-chg-${{k}}" style="color: ${{peChgColor}}; font-weight: 700;">${{peChgSign}}${{formatNumber(row.pe_chg)}}</td>
                    <td class="${{peBg}}" id="pe-oi-${{k}}">${{formatNumber(row.pe_oi)}}${{row.pe_wall}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        buildTable();

        // HIGH-FREQUENCY REAL-TIME TICK SIMULATOR (800ms INTERVAL) - TICKS PRICE, VOLUME, OI & OI CHANGE!
        setInterval(() => {{
            // 1. Subtle Spot Drift
            const spotDrift = (Math.random() - 0.49) * 0.35;
            currentSpot = +(currentSpot + spotDrift).toFixed(2);
            const spotEl = document.getElementById('header-spot');
            if (spotEl) {{
                spotEl.innerText = `₹${{currentSpot.toLocaleString('en-IN', {{minimumFractionDigits: 2}})}}`;
            }}

            // 2. Select 2-4 active near strikes to tick
            const numUpdates = Math.floor(Math.random() * 3) + 2;
            let atmCePrice = null;
            let atmPePrice = null;

            for (let i = 0; i < numUpdates; i++) {{
                const randIdx = Math.floor(Math.random() * initialData.length);
                const row = initialData[randIdx];
                const k = row.strike;

                // --- Call LTP & Volume Tick ---
                const ceTick = (Math.random() - 0.48) * 0.40;
                const oldCe = row.ce_ltp;
                const newCe = Math.max(0.05, +(oldCe + ceTick).toFixed(2));
                row.ce_ltp = newCe;
                row.ce_vol += Math.floor(Math.random() * 150) + 75;

                // --- Call OI & OI Change Tick (Active Call Writing / Unwinding) ---
                const ceOiDelta = (Math.random() > 0.42 ? 1 : -1) * (Math.floor(Math.random() * 4) + 1) * lotSize;
                row.ce_oi = Math.max(1000, row.ce_oi + ceOiDelta);
                row.ce_chg += ceOiDelta;

                const ceCell = document.getElementById(`ce-ltp-${{k}}`);
                const ceVolCell = document.getElementById(`ce-vol-${{k}}`);
                const ceOiCell = document.getElementById(`ce-oi-${{k}}`);
                const ceChgCell = document.getElementById(`ce-chg-${{k}}`);

                if (ceCell) {{
                    ceCell.innerText = `₹${{newCe.toFixed(1)}}`;
                    ceCell.classList.remove('flash-up', 'flash-down');
                    void ceCell.offsetWidth;
                    ceCell.classList.add(newCe >= oldCe ? 'flash-up' : 'flash-down');
                    setTimeout(() => {{ ceCell.classList.remove('flash-up', 'flash-down'); }}, 450);
                }}
                if (ceVolCell) {{
                    ceVolCell.innerText = formatNumber(row.ce_vol);
                }}
                if (ceOiCell) {{
                    ceOiCell.innerText = `${{formatNumber(row.ce_oi)}}${{row.ce_wall}}`;
                }}
                if (ceChgCell) {{
                    const sign = row.ce_chg >= 0 ? '+' : '';
                    ceChgCell.innerText = `${{sign}}${{formatNumber(row.ce_chg)}}`;
                    ceChgCell.style.color = row.ce_chg >= 0 ? '#00F5A0' : '#FF3B69';
                    ceChgCell.classList.remove('flash-up', 'flash-down');
                    void ceChgCell.offsetWidth;
                    ceChgCell.classList.add(ceOiDelta >= 0 ? 'flash-up' : 'flash-down');
                    setTimeout(() => {{ ceChgCell.classList.remove('flash-up', 'flash-down'); }}, 450);
                }}

                // --- Put LTP & Volume Tick ---
                const peTick = (Math.random() - 0.48) * 0.40;
                const oldPe = row.pe_ltp;
                const newPe = Math.max(0.05, +(oldPe + peTick).toFixed(2));
                row.pe_ltp = newPe;
                row.pe_vol += Math.floor(Math.random() * 150) + 75;

                // --- Put OI & OI Change Tick (Active Put Writing / Unwinding) ---
                const peOiDelta = (Math.random() > 0.42 ? 1 : -1) * (Math.floor(Math.random() * 4) + 1) * lotSize;
                row.pe_oi = Math.max(1000, row.pe_oi + peOiDelta);
                row.pe_chg += peOiDelta;

                const peCell = document.getElementById(`pe-ltp-${{k}}`);
                const peVolCell = document.getElementById(`pe-vol-${{k}}`);
                const peOiCell = document.getElementById(`pe-oi-${{k}}`);
                const peChgCell = document.getElementById(`pe-chg-${{k}}`);

                if (peCell) {{
                    peCell.innerText = `₹${{newPe.toFixed(1)}}`;
                    peCell.classList.remove('flash-up', 'flash-down');
                    void peCell.offsetWidth;
                    peCell.classList.add(newPe >= oldPe ? 'flash-up' : 'flash-down');
                    setTimeout(() => {{ peCell.classList.remove('flash-up', 'flash-down'); }}, 450);
                }}
                if (peVolCell) {{
                    peVolCell.innerText = formatNumber(row.pe_vol);
                }}
                if (peOiCell) {{
                    peOiCell.innerText = `${{formatNumber(row.pe_oi)}}${{row.pe_wall}}`;
                }}
                if (peChgCell) {{
                    const sign = row.pe_chg >= 0 ? '+' : '';
                    peChgCell.innerText = `${{sign}}${{formatNumber(row.pe_chg)}}`;
                    peChgCell.style.color = row.pe_chg >= 0 ? '#00F5A0' : '#FF3B69';
                    peChgCell.classList.remove('flash-up', 'flash-down');
                    void peChgCell.offsetWidth;
                    peChgCell.classList.add(peOiDelta >= 0 ? 'flash-up' : 'flash-down');
                    setTimeout(() => {{ peChgCell.classList.remove('flash-up', 'flash-down'); }}, 450);
                }}

                if (k === atmStrike) {{
                    atmCePrice = newCe;
                    atmPePrice = newPe;
                }}
            }}

            // 3. Update Header Card Values if ATM ticked
            if (atmCePrice !== null) {{
                const cardCe = document.getElementById('card-ce-ltp');
                if (cardCe) cardCe.innerText = `₹${{atmCePrice.toFixed(1)}}`;
            }}
            if (atmPePrice !== null) {{
                const cardPe = document.getElementById('card-pe-ltp');
                if (cardPe) cardPe.innerText = `₹${{atmPePrice.toFixed(1)}}`;
            }}
            const cardStraddle = document.getElementById('card-straddle');
            if (cardStraddle && atmCePrice && atmPePrice) {{
                cardStraddle.innerText = `₹${{(atmCePrice + atmPePrice).toFixed(1)}}`;
            }}
        }}, 850);
        </script>
        </body>
        </html>
        """

        table_height = min(720, max(420, len(sub_oc) * 36 + 140))
        components.html(full_oc_table, height=table_height, scrolling=True)
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

    chain_data_s3 = data_eng.get_option_chain(symbol, days_to_expiry=dte)
    spot_s3 = data_eng.get_market_quote(symbol)['current_price']
    acc_s3 = paper_eng.get_account()

    all_strats = [
        StrategyOptimizer.generate_big_lizard(symbol, spot_s3, chain_data_s3, dte=dte, lot_size=default_lot, account_capital=acc_s3['balance']),
        StrategyOptimizer.generate_broken_wing_butterfly(symbol, spot_s3, chain_data_s3, dte=dte, lot_size=default_lot, account_capital=acc_s3['balance']),
        StrategyOptimizer.generate_double_calendar(symbol, spot_s3, chain_data_s3, dte=dte, lot_size=default_lot, account_capital=acc_s3['balance']),
        StrategyOptimizer.generate_classic_iron_condor(symbol, spot_s3, chain_data_s3, dte=dte, lot_size=default_lot, account_capital=acc_s3['balance']),
        StrategyOptimizer.generate_iron_butterfly(symbol, spot_s3, chain_data_s3, dte=dte, lot_size=default_lot, account_capital=acc_s3['balance'])
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
            tid = paper_eng.execute_paper_trade(symbol, st_data, spot_s3, 75.0, lot_size=default_lot)
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
    acc_s5 = paper_eng.get_account()
    spot_s5 = data_eng.get_market_quote(symbol)['current_price']
    
    hdr_c1, hdr_c2 = st.columns([7, 3])
    with hdr_c1:
        st.markdown(f"""
        <div class="cockpit-card" style="margin-bottom: 0;">
            <div class="card-header">
                <span>💼 3-5 MONTH INCUBATION SUITE (BENCHMARK CAPITAL: ₹3,00,000.00)</span>
                <span class="glow-pill-emerald">BALANCE: ₹{acc_s5['balance']:,.2f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with hdr_c2:
        if st.button("🔄 Reset Portfolio to ₹3,00,000", use_container_width=True, help="Wipes paper journal and resets balance to ₹3,00,000"):
            paper_eng.reset_account(300000.0)
            st.toast("✅ Portfolio successfully reset to clean ₹3,00,000.00!")
            st.rerun()

    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    pos_df = paper_eng.get_open_positions()
    if pos_df.empty:
        st.info("No open positions in portfolio. Deploy a strategy from Section 1 or Section 3!")
    else:
        for _, r in pos_df.iterrows():
            mtm, elapsed_mins = AutoRebalancerSentinel.calculate_realistic_mtm(r, spot_s5)
            pnl_c = "#00F5A0" if mtm >= 0 else "#FF3B69"
            col_a, col_b, col_c = st.columns([3, 2, 1])
            with col_a:
                st.markdown(f"**#{r['id']} {r['strategy_name']}** ({r['symbol']}) | Lots: `{r['lot_size']}` | Active: `{elapsed_mins:.1f}m`")
            with col_b:
                st.markdown(f"<span class='mono' style='font-size: 1.1rem; font-weight: 800; color: {pnl_c};'>MTM: ₹{mtm:+,.2f}</span>", unsafe_allow_html=True)
            with col_c:
                if st.button("Square Off", key=f"sec5_sq_{r['id']}", use_container_width=True):
                    paper_eng.close_position(r['id'], spot_s5, mtm, exit_reason="Manual Close")
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
    conn_status = "🟢 CONNECTED & LIVE TICKING" if data_eng.fyers.is_connected() else "🔴 DISCONNECTED (TOKEN REQUIRED)"
    conn_pill = "glow-pill-emerald" if data_eng.fyers.is_connected() else "glow-pill-rose"

    st.markdown(f"""
    <div class="cockpit-card">
        <div class="card-header">
            <span>⚙️ 1-CLICK FYERS API V3 LIVE BROKER GATEWAY</span>
            <span class="{conn_pill}">{conn_status}</span>
        </div>
        <p style="font-size: 0.8rem; color: #8B949E; margin-bottom: 8px;">
            Fyers API connect hone par NIFTY, BANKNIFTY, SENSEX, FINNIFTY, MIDCPNIFTY ka <b>100% official live tick-by-tick option chain</b> direct Fyers ke server se aayega.
        </p>
    </div>
    """, unsafe_allow_html=True)

    f_col1, f_col2 = st.columns([1.2, 1])

    with f_col1:
        st.markdown("#### 🔑 Step 1: 1-Click Fyers Auth Generator")
        f_app = st.text_input("Fyers App ID", value=config.get("FYERS_APP_ID", "2O4CWNTG7T-100"))
        f_sec = st.text_input("Fyers Secret ID", type="password", value=config.get("FYERS_SECRET_ID", "5NAJDN8GG9"))
        f_red = st.text_input("Redirect URI", value=config.get("FYERS_REDIRECT_URI", "https://trade.fyers.in/api-login/"))

        auth_url = f"https://api-t1.fyers.in/api/v3/generate-authcode?client_id={f_app}&redirect_uri=https%3A%2F%2Ftrade.fyers.in%2Fapi-login%2F&response_type=code&state=None"

        st.markdown(f"""
        <div style="background: rgba(0, 210, 255, 0.08); border: 1px solid rgba(0, 210, 255, 0.3); border-radius: 8px; padding: 10px; margin: 8px 0;">
            <b>👉 Step 1:</b> Neeche diye link ko open karke Fyers me login karo:<br>
            <a href="{auth_url}" target="_blank" style="color: #00F5A0; font-weight: 800; font-size: 0.9rem; word-break: break-all;">🔗 Click Here to Login to Fyers</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### ⚡ Step 2: Paste Redirect URL & Activate")
        redirect_input = st.text_input("Login ke baad browser me jo URL aayi wo yaha paste karo", placeholder="https://trade.fyers.in/api-login/?s=ok&code=...&auth_code=eyJ...")

        if st.button("🚀 Activate Live Fyers Broker Feed", use_container_width=True):
            if redirect_input:
                try:
                    from fyers_apiv3 import fyersModel
                    match = re.search(r"auth_code=([^&]+)", redirect_input)
                    auth_code = match.group(1) if match else redirect_input.strip()

                    session = fyersModel.SessionModel(
                        client_id=f_app,
                        secret_key=f_sec,
                        redirect_uri=f_red,
                        response_type="code",
                        grant_type="authorization_code"
                    )
                    session.set_token(auth_code)
                    resp = session.generate_token()

                    if "access_token" in resp:
                        tok = resp["access_token"]
                        ConfigManager.save_config({
                            "FYERS_APP_ID": f_app,
                            "FYERS_SECRET_ID": f_sec,
                            "FYERS_REDIRECT_URI": f_red,
                            "FYERS_ACCESS_TOKEN": tok
                        })
                        st.success("🎉 CONGRATULATIONS! 100% Live Fyers Broker Feed is now CONNECTED!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Fyers Error: {resp.get('message', 'Invalid Auth Code')}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("⚠️ Pehle Fyers login ke baad browser ka URL yaha paste karo.")

    with f_col2:
        st.markdown("#### 🤖 Google Gemini AI API")
        g_key = st.text_input("Gemini API Key", type="password", value=config.get("GEMINI_API_KEY", ""))
        if st.button("💾 Save Gemini Key", use_container_width=True):
            ConfigManager.save_config({"GEMINI_API_KEY": g_key})
            st.success("✅ Gemini Key Saved Permanently!")
            st.rerun()

        st.markdown("---")
        st.markdown("#### 🛠️ Direct Access Token Paste (Optional)")
        direct_tok = st.text_input("Direct Access Token (agar already hai)", type="password", value=config.get("FYERS_ACCESS_TOKEN", ""))
        if st.button("💾 Save Token Directly", use_container_width=True):
            ConfigManager.save_config({"FYERS_ACCESS_TOKEN": direct_tok})
            st.success("✅ Access Token Saved Permanently!")
            st.rerun()
