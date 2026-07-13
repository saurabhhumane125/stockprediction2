import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import type { HistoryItem } from "../types/history.view.types";

interface HistoryTableProps {
  history: HistoryItem[];
}

const columns = [
  { key: "symbol", label: "Stock" },
  { key: "prediction", label: "Prediction" },
  { key: "confidence", label: "Confidence" },
  { key: "probabilityBuy", label: "Buy %" },
  { key: "probabilitySell", label: "Sell %" },
  { key: "createdAt", label: "Date & Time" },
];

export function HistoryTable({ history }: Readonly<HistoryTableProps>) {
  return (
    <Card padding="none">
      <div className="px-6 py-5 border-b border-[#F0F4F8]">
        <h2 className="text-lg font-bold text-[#11131A] tracking-tight font-[family-name:var(--font-space-grotesk)]">Prediction History</h2>
        <p className="mt-1 text-[14px] text-[#5B6473]">
          {history.length} records found
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="border-b border-[#F0F4F8] bg-[#F7F9FC]">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-6 py-4 text-left text-[13px] font-bold uppercase tracking-[0.06em] text-[#8B95A5] whitespace-nowrap"
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#F0F4F8]">
            {history.map((row) => (
              <tr
                key={row.id}
                className="transition-colors duration-100 hover:bg-[#FAFBFC]"
              >
                <td className="px-6 py-4">
                  <span className="text-[15px] font-bold text-[#11131A]">
                    {row.symbol}
                  </span>
                </td>

                <td className="px-6 py-4">
                  <Badge
                    variant={
                      row.prediction === "BUY"
                        ? "buy"
                        : row.prediction === "SELL"
                        ? "sell"
                        : "hold"
                    }
                  >
                    {row.prediction}
                  </Badge>
                </td>

                <td className="px-6 py-4">
                  <span className="text-[15px] font-bold text-[#11131A] font-tabular">
                    {(row.confidence * 100).toFixed(1)}%
                  </span>
                </td>

                <td className="px-6 py-4">
                  <span className="text-[15px] text-[#5B6473] font-tabular font-medium">
                    {row.probabilityBuy === null
                      ? "—"
                      : `${(row.probabilityBuy * 100).toFixed(1)}%`}
                  </span>
                </td>

                <td className="px-6 py-4">
                  <span className="text-[15px] text-[#5B6473] font-tabular font-medium">
                    {row.probabilitySell === null
                      ? "—"
                      : `${(row.probabilitySell * 100).toFixed(1)}%`}
                  </span>
                </td>

                <td className="px-6 py-4">
                  <span className="text-[15px] text-[#5B6473] whitespace-nowrap font-medium">
                    {new Date(row.createdAt).toLocaleString()}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}