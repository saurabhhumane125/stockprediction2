from app.core import market_rules


class MarketRegimeService:

    def determine_trend(
        self,
        features: dict,
    ) -> str:

        if (
            features["EMA20"]
            >
            features["EMA50"]
        ):

            return "BULLISH"

        if (
            features["EMA20"]
            <
            features["EMA50"]
        ):

            return "BEARISH"

        return "SIDEWAYS"

    def determine_trend_strength(
        self,
        features: dict,
    ) -> str:

        adx = features["ADX"]

        if (
            adx >=
            market_rules.ADX_STRONG_TREND
        ):

            return "STRONG"

        if (
            adx >=
            market_rules.ADX_MODERATE_TREND
        ):

            return "MODERATE"

        return "WEAK"

    def determine_volatility(
        self,
        features: dict,
    ) -> str:

        volatility = features[
            "VOLATILITY"
        ]

        if (
            volatility >=
            market_rules.HIGH_VOLATILITY
        ):

            return "HIGH"

        if (
            volatility <=
            market_rules.LOW_VOLATILITY
        ):

            return "LOW"

        return "NORMAL"

    def determine_momentum(
        self,
        features: dict,
    ) -> str:

        roc = features["ROC"]

        if (
            roc >
            market_rules.POSITIVE_ROC
        ):

            return "POSITIVE"

        if (
            roc <
            market_rules.NEGATIVE_ROC
        ):

            return "NEGATIVE"

        return "NEUTRAL"

    def determine_regime(
        self,
        trend: str,
        strength: str,
        volatility: str,
    ) -> str:

        if (
            trend == "BULLISH"
            and strength == "STRONG"
        ):

            return "STRONG_BULLISH"

        if (
            trend == "BEARISH"
            and strength == "STRONG"
        ):

            return "STRONG_BEARISH"

        if (
            trend == "BULLISH"
        ):

            return "BULLISH"

        if (
            trend == "BEARISH"
        ):

            return "BEARISH"

        if (
            volatility == "HIGH"
        ):

            return "HIGH_VOLATILITY"

        return "SIDEWAYS"

    def analyze(
        self,
        features: dict,
    ):

        trend = self.determine_trend(
            features
        )

        strength = (
            self.determine_trend_strength(
                features
            )
        )

        volatility = (
            self.determine_volatility(
                features
            )
        )

        momentum = (
            self.determine_momentum(
                features
            )
        )

        regime = (
            self.determine_regime(
                trend,
                strength,
                volatility,
            )
        )

        return {

            "regime": regime,

            "trend": trend,

            "trend_strength": strength,

            "volatility": volatility,

            "momentum": momentum,

        }


market_regime_service = (
    MarketRegimeService()
)