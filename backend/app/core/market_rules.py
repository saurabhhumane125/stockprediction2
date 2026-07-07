"""
Centralized market interpretation rules.

Every service that interprets technical indicators
must import thresholds from this file.

Do NOT hardcode values in services.
"""


# RSI

RSI_OVERBOUGHT = 70.0

RSI_OVERSOLD = 30.0


# ADX

ADX_STRONG_TREND = 25.0

ADX_MODERATE_TREND = 20.0


# Volatility

HIGH_VOLATILITY = 0.020

LOW_VOLATILITY = 0.005


# ROC

POSITIVE_ROC = 0.0

NEGATIVE_ROC = 0.0


# Volume Change

POSITIVE_VOLUME_CHANGE = 0.0

NEGATIVE_VOLUME_CHANGE = 0.0