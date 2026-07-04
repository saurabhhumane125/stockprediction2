import os

from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv(
    "NEWS_API_KEY"
)

if NEWS_API_KEY is None:

    raise ValueError(
        "NEWS_API_KEY missing."
    )