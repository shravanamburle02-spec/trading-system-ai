"""
Master Trading System - Voice AI Co-Pilot ("Trading Dost" in Hinglish)
Provides conversational Hinglish commentary, emotional guardrails against FOMO/revenge trading,
and automated Post-Market Audio Reviews using free ultra-natural Edge-TTS speech synthesis.
"""

import os
import asyncio
import edge_tts

class VoiceAICopilot:
    VOICE = "hi-IN-MadhurNeural" # Natural Hinglish / Hindi voice

    @classmethod
    async def _generate_audio_file(cls, text, output_path="temp_voice.mp3"):
        """Asynchronously converts Hinglish text into natural MP3 audio using Edge-TTS."""
        try:
            communicate = edge_tts.Communicate(text, cls.VOICE)
            await communicate.save(output_path)
            return output_path
        except Exception as e:
            return None

    @classmethod
    def speak_text(cls, text, output_path="temp_voice.mp3"):
        """Synchronous wrapper to generate audio file."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            res = loop.run_until_complete(cls._generate_audio_file(text, output_path))
            loop.close()
            return res
        except Exception as e:
            return None

    @classmethod
    def get_live_market_commentary(cls, symbol, spot, confluence, smc_data, strategy_dict):
        """Generates Hinglish friendly commentary on the current market setup."""
        bias = confluence['market_bias']
        score = confluence['composite_score']
        conf_pct = confluence['confluence_pct']
        strat_name = strategy_dict.get('strategy_name', 'Setup')

        if 'BULLISH' in bias:
            text = (
                f"Bhai, {symbol} abhi {spot:.0f} ke aas-paas trade kar raha hai. "
                f"Derivatives, Indicators aur Smart Money teeno milkar {conf_pct:.0f}% ka strong Bullish Confluence de rahe hain. "
                f"SMC chart pe fresh Demand Order Block defend ho raha hai. "
                f"Is waqt humare liye best setup '{strat_name}' rahega. "
                f"Stop-loss strict rakhna aur disciplined rehna bhai!"
            )
        elif 'BEARISH' in bias:
            text = (
                f"Bhai, {symbol} mein {spot:.0f} par Supply Zone se rejection dikh raha hai. "
                f"Confluence Score {conf_pct:.0f}% Bearish hai aur Call writing heavy hai. "
                f"Smart Money ka Change of Character indicate ho raha hai. "
                f"Humare liye '{strat_name}' ka setup ready hai. "
                f"Hedge leg ke bina entry mat lena!"
            )
        else:
            text = (
                f"Bhai sun, {symbol} abhi range-bound phase mein hai aur market dono taraf trap kar sakta hai. "
                f"Directional entry lene ka koi fayda nahi hai. "
                f"Maine range probability ke hisab se custom Non-Directional Iron Condor design kiya hai jisme dono side safety margin hai. "
                f"Chop market mein safe theta decay capture karte hain!"
            )

        return text

    @classmethod
    def get_emotional_guardrail_message(cls, reason_type="DAILY_LOSS_LIMIT"):
        """Voice warning to prevent emotional / revenge trading."""
        if reason_type == "DAILY_LOSS_LIMIT":
            return (
                "Bhai bas kar! Aaj ka Daily Loss Limit hit ho chuka hai. "
                "Abhi screen band kar aur bahar ghoomne nikal ja. "
                "Market kahin bhag nahi raha, kal fresh mind se profitable trade karenge. "
                "Revenge trading bilkul allowed nahi hai!"
            )
        elif reason_type == "FOMO_ALERT":
            return (
                "Bhai rukh ja! Ekdum se rally dekh kar green candle ke top par mat kood. "
                "Yeh Smart Money ka Liquidity Trap ho sakta hai. "
                "Pullback ka wait kar aur Order Block retest par hi disciplined entry le."
            )
        else:
            return (
                "Bhai trade lene se pehle apna risk calculate kar le. "
                "Rule number one: Capital protection sabse pehle, profit baad mein!"
            )

    @classmethod
    def get_post_market_review(cls, journal_df, account_summary):
        """Generates end-of-day audio review summary."""
        total_pnl = account_summary['realized_pnl']
        num_trades = len(journal_df) if journal_df is not None else 0

        if total_pnl >= 0:
            text = (
                f"Bhai shabash! Aaj humne total {num_trades} trades execute kiye aur net profit ₹{total_pnl:,.2f} raha. "
                f"3-layer confluence system follow karne ka yahi faayda hai. "
                f"Disciplined trading continue rakho aur kal subah live market mein milte hain!"
            )
        else:
            text = (
                f"Bhai aaj ka din thoda tough raha aur net PnL ₹{total_pnl:,.2f} raha. "
                f"Lekin sabse achi baat yeh rahi ki humne risk guardrails follow kiye aur capital bacha liya. "
                f"Loss trading ka ek part hai. Rest karo aur kal naye setups par kaam karenge!"
            )

        return text
