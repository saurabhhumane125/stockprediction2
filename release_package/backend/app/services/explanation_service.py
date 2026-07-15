from app.core import market_rules
class ExplanationService:

    def analyze_trend(
        self,
        features: dict,
    ) -> dict:

        ema20 = features["EMA20"]
        ema50 = features["EMA50"]
        adx = features["ADX"]

        if ema20 > ema50:
            trend = "Bullish"
        elif ema20 < ema50:
            trend = "Bearish"
        else:
            trend = "Sideways"

        if adx >= market_rules.ADX_STRONG_TREND:
            strength = "Strong"
        elif adx >= market_rules.ADX_MODERATE_TREND:
            strength = "Moderate"
        else:
            strength = "Weak"

        return {
            "trend": trend,
            "trend_strength": strength,
        }

    def analyze_momentum(
        self,
        features: dict,
    ) -> dict:

        rsi = features["RSI"]
        roc = features["ROC"]
        momentum = features["MOMENTUM"]

        if rsi >= market_rules.RSI_OVERBOUGHT:
            rsi_state = "Overbought"
        elif rsi <= market_rules.RSI_OVERSOLD:
            rsi_state = "Oversold"
        else:
            rsi_state = "Neutral"

        return {
            "rsi": round(rsi, 2),
            "rsi_state": rsi_state,
            "roc": round(roc, 2),
            "momentum": round(momentum, 2),
        }

    def analyze_volatility(
        self,
        features: dict,
    ) -> dict:

        volatility = features["VOLATILITY"]
        atr = features["ATR"]
        bb_width = features["BB_WIDTH"]

        return {
            "volatility": round(volatility, 6),
            "atr": round(atr, 2),
            "bollinger_width": round(bb_width, 2),
        }

    def analyze_price_position(
        self,
        features: dict,
    ) -> dict:

        close = features["Close"]
        upper = features["BB_UPPER"]
        lower = features["BB_LOWER"]

        if close >= upper:
            position = "Above Upper Band"
        elif close <= lower:
            position = "Below Lower Band"
        else:
            position = "Inside Bands"

        return {
            "price_position": position,
        }

    def analyze_volume(
        self,
        features: dict,
    ) -> dict:

        volume_change = features["VOLUME_CHANGE"]

        if volume_change > 0:
            direction = "Increasing"
        elif volume_change < 0:
            direction = "Decreasing"
        else:
            direction = "Stable"

        return {
            "volume_change": round(volume_change, 4),
            "volume_trend": direction,
        }

    def generate_summary(
        self,
        trend: dict,
        momentum: dict,
        volatility: dict,
        price: dict,
        volume: dict,
    ) -> list[str]:

        summary = []

        summary.append(
            f"Trend is {trend['trend']} with {trend['trend_strength']} strength."
        )

        summary.append(
            f"RSI is {momentum['rsi']:.2f} ({momentum['rsi_state']})."
        )

        summary.append(
            f"ROC is {momentum['roc']:.2f} and momentum is {momentum['momentum']:.2f}."
        )

        summary.append(
            f"Price is {price['price_position']}."
        )

        summary.append(
            f"Volume trend is {volume['volume_trend']}."
        )

        summary.append(
            f"ATR is {volatility['atr']:.2f} with Bollinger Band width {volatility['bollinger_width']:.2f}."
        )

        return summary

    def explain(
        self,
        features: dict,
    ) -> dict:

        trend = self.analyze_trend(features)

        momentum = self.analyze_momentum(features)

        volatility = self.analyze_volatility(features)

        price = self.analyze_price_position(features)

        volume = self.analyze_volume(features)

        summary = self.generate_summary(
            trend,
            momentum,
            volatility,
            price,
            volume,
        )

        return {

            **trend,

            **momentum,

            **volatility,

            **price,

            **volume,

            "summary": summary,

        }


explanation_service = ExplanationService()