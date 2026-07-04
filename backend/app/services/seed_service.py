from sqlalchemy.orm import Session

from app.models import Stock


class SeedService:

    STOCKS = [
        ("RELIANCE", "Reliance Industries", "Energy"),
        ("TCS", "Tata Consultancy Services", "IT"),
        ("INFY", "Infosys", "IT"),
        ("HDFCBANK", "HDFC Bank", "Banking"),
        ("ICICIBANK", "ICICI Bank", "Banking"),
        ("SBIN", "State Bank of India", "Banking"),
        ("LT", "Larsen & Toubro", "Infrastructure"),
        ("ITC", "ITC Limited", "FMCG"),
        ("HINDUNILVR", "Hindustan Unilever", "FMCG"),
        ("BHARTIARTL", "Bharti Airtel", "Telecom"),
    ]

    def seed_stocks(self, db: Session):

        for symbol, company, sector in self.STOCKS:

            exists = (
                db.query(Stock)
                .filter(Stock.symbol == symbol)
                .first()
            )

            if exists:
                continue

            db.add(
                Stock(
                    symbol=symbol,
                    company_name=company,
                    sector=sector,
                )
            )

        db.commit()


seed_service = SeedService()