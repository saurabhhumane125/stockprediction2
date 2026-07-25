from sqlalchemy.orm import Session

from app.models import Stock

from app.adapters.universe_adapter import universe_adapter

class SeedService:

    def seed_stocks(self, db: Session):
        
        metadata_list = universe_adapter.get_active_universe_metadata()

        for metadata in metadata_list:
            symbol = metadata["symbol"]
            company = metadata["company_name"]
            sector = metadata["sector"]

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