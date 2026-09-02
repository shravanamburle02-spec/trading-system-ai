"""
Master Trading System - 3-Layer Confluence Engine
Merges Derivatives Data (35%), Technical Indicators (30%), and Smart Money Concepts (35%)
into a unified Confluence Score and optimal Strategy Recommendation.
"""

import numpy as np

class ConfluenceEngine:
    @staticmethod
    def calculate_data_score(chain_data, fii_dii):
        """Calculates Data Score (-100 to +100) from OI, PCR, Max Pain & Institutions."""
        pcr = chain_data.get('pcr', 1.0)
        spot = chain_data.get('spot_price', 25000.0)
        max_pain = chain_data.get('max_pain', 25000.0)
        total_ce = chain_data.get('total_ce_oi', 1)
        total_pe = chain_data.get('total_pe_oi', 1)
        
        score = 0
        reasons = []

        # 1. PCR Analysis (35 pts)
        if pcr >= 1.30:
            score += 35
            reasons.append(f"Bullish High PCR ({pcr}) - Heavy Put Writing Support (+35)")
        elif pcr >= 1.05:
            score += 20
            reasons.append(f"Mildly Bullish PCR ({pcr}) (+20)")
        elif pcr <= 0.70:
            score -= 35
            reasons.append(f"Bearish Low PCR ({pcr}) - Heavy Call Writing Resistance (-35)")
        elif pcr <= 0.90:
            score -= 20
            reasons.append(f"Mildly Bearish PCR ({pcr}) (-20)")
        else:
            reasons.append(f"Neutral PCR ({pcr}) (0)")

        # 2. Max Pain vs Spot (30 pts)
        pain_diff = (max_pain - spot) / spot
        if pain_diff > 0.004:
            score += 30
            reasons.append(f"Spot is below Max Pain ({max_pain}) - Expiry Gravity Pull Up (+30)")
        elif pain_diff < -0.004:
            score -= 30
            reasons.append(f"Spot is above Max Pain ({max_pain}) - Expiry Gravity Pull Down (-30)")
        else:
            reasons.append(f"Spot near Max Pain ({max_pain}) - Pinning Expected (0)")

        # 3. Institutional FII/DII flow (35 pts)
        bias = fii_dii.get('institutional_bias', 'Neutral')
        if 'Bullish' in bias:
            score += 35
            reasons.append("FII/DII Net Positioning is Bullish (+35)")
        elif 'Bearish' in bias:
            score -= 35
            reasons.append("FII/DII Net Positioning is Bearish (-35)")
        else:
            reasons.append("FII/DII Positioning is Balanced (0)")

        return {
            'data_score': max(-100, min(100, score)),
            'reasons': reasons
        }

    @classmethod
    def evaluate(cls, chain_data, indicator_data, smc_data, fii_dii):
        """Cross-evaluates all 3 layers and produces the final Master Confluence Verdict."""
        data_res = cls.calculate_data_score(chain_data, fii_dii)
        data_score = data_res['data_score']
        ind_score = indicator_data['indicator_score']
        smc_score = smc_data['smc_score']

        # Weighted Composite Score
        # Data: 35%, Indicators: 30%, SMC: 35%
        composite = (data_score * 0.35) + (ind_score * 0.30) + (smc_score * 0.35)
        
        # Absolute Confluence percentage (Agreement strength)
        signs = [int(np.sign(data_score)), int(np.sign(ind_score)), int(np.sign(smc_score))]
        agree_count = max(signs.count(1), signs.count(-1))
        
        if agree_count == 3:
            confluence_pct = 85 + (abs(composite) / 100.0) * 15  # 85% - 100%
            agreement_status = "🔥 3-Layer FULL CONFLUENCE (Data + Indicators + SMC in 100% Agreement)"
        elif agree_count == 2:
            confluence_pct = 65 + (abs(composite) / 100.0) * 15  # 65% - 80%
            agreement_status = "⚡ 2-Layer Confluence (Majority Directional Agreement)"
        else:
            confluence_pct = 40 + (abs(composite) / 100.0) * 15  # 40% - 55%
            agreement_status = "⚖️ Mixed / Conflicting Layers (Market Range-Bound & Chop Risk)"

        # Determine Market Bias & Strategy Type
        if composite >= 40:
            bias = "STRONG BULLISH"
            strat_mode = "DIRECTIONAL (BULLISH)"
            recommended_timeframe = "Intraday Momentum / Expiry Buy" if confluence_pct >= 75 else "Pullback Dip Buying (Swing)"
        elif composite >= 15:
            bias = "MODERATE BULLISH"
            strat_mode = "DIRECTIONAL (BULLISH CREDIT SPREAD)"
            recommended_timeframe = "Intraday / Multi-Day Positional"
        elif composite <= -40:
            bias = "STRONG BEARISH"
            strat_mode = "DIRECTIONAL (BEARISH)"
            recommended_timeframe = "Intraday Momentum / Expiry Sell" if confluence_pct >= 75 else "Rally Selling (Swing)"
        elif composite <= -15:
            bias = "MODERATE BEARISH"
            strat_mode = "DIRECTIONAL (BEAR CALL SPREAD)"
            recommended_timeframe = "Intraday / Multi-Day Positional"
        else:
            bias = "NEUTRAL / RANGE-BOUND"
            strat_mode = "DYNAMIC NON-DIRECTIONAL (CUSTOM STRANGLE / IRON CONDOR)"
            recommended_timeframe = "Expiry-Based Multi-Day / Positional"

        return {
            'composite_score': round(float(composite), 2),  # -100 to +100
            'confluence_pct': round(float(confluence_pct), 1), # 0 to 100%
            'market_bias': bias,
            'strat_mode': strat_mode,
            'recommended_timeframe': recommended_timeframe,
            'agreement_status': agreement_status,
            'layer_scores': {
                'data_score': data_score,
                'indicator_score': ind_score,
                'smc_score': smc_score
            },
            'all_reasons': {
                'data_reasons': data_res['reasons'],
                'indicator_reasons': indicator_data['reasons'],
                'smc_reasons': smc_data['reasons']
            }
        }
