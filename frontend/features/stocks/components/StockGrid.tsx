import type {

  StockViewModel,

} from "../types/stock.view.types";

import { StockCard } from "./StockCard";

interface StockGridProps {

  stocks: StockViewModel[];

}

export function StockGrid({

  stocks,

}: Readonly<StockGridProps>) {

  return (

    <div className="grid grid-cols-12 gap-6">

      {stocks.map(

        (stock) => (

          <div

            key={stock.id}

            className="col-span-12 md:col-span-6 xl:col-span-4"

          >

            <StockCard

              stock={stock}

            />

          </div>

        ),

      )}

    </div>

  );

}