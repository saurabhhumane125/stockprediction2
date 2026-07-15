from sqlalchemy.orm import Session

from app.models import Stock


class StockService:

    def get_all(self, db: Session):

        return (
            db.query(Stock)
            .order_by(Stock.symbol)
            .all()
        )

    def get_by_symbol(
        self,
        db: Session,
        symbol: str,
    ):

        return (
            db.query(Stock)
            .filter(
                Stock.symbol == symbol.upper()
            )
            .first()
        )


stock_service = StockService()