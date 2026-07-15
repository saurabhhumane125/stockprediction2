from datetime import datetime

from newsapi import NewsApiClient
from sqlalchemy.orm import Session
from app.core.logger import logger

from app.config import settings
from app.models import News, Stock
from app.services.sentiment_service import sentiment_service


class NewsService:

    def __init__(self):

        self.client = NewsApiClient(
            api_key=settings.NEWS_API_KEY
        )

    def sync_news(
        self,
        db: Session,
        symbol: str,
    ):

        stock = (
            db.query(Stock)
            .filter(
                Stock.symbol == symbol.upper()
            )
            .first()
        )

        if stock is None:
            raise ValueError(
                "Stock not found."
            )

        response = self.client.get_everything(
            q=f'"{stock.company_name}" OR {stock.symbol}',
            language="en",
            sort_by="publishedAt",
            page_size=50,
        )

        articles = response.get(
            "articles",
            [],
        )

        company = stock.company_name.lower()
        ticker = stock.symbol.lower()

        inserted = 0

        for article in articles:

            title = article.get(
                "title",
                "",
            )

            title_lower = title.lower()

            if (
                company not in title_lower
                and ticker not in title_lower
            ):
                continue

            url = article.get("url")

            if not url:
                continue

            exists = (
                db.query(News)
                .filter(
                    News.url == url
                )
                .first()
            )

            if exists:
                continue

            sentiment = (
                sentiment_service.analyze(
                    title
                )
            )

            published = article.get(
                "publishedAt"
            )

            if published:

                published_at = datetime.fromisoformat(
                    published.replace(
                        "Z",
                        "+00:00",
                    )
                )

            else:

                published_at = datetime.utcnow()

            db.add(
                News(
                    stock_id=stock.id,
                    title=title,
                    source=article["source"]["name"],
                    url=url,
                    published_at=published_at,
                    sentiment=sentiment["sentiment"],
                    sentiment_score=sentiment["score"],
                )
            )

            inserted += 1

        db.commit()

        return inserted

        logger.info(
            f"News synchronized for {symbol}"
        )


news_service = NewsService()