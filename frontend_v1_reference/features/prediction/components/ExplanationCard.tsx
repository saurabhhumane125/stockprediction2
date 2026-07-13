import { Card, CardContent, CardLabel } from "@/components/ui/Card";
import type { PredictionViewModel } from "../types/prediction.view.types";

interface ExplanationCardProps {
  prediction: PredictionViewModel;
}

interface MetricItemProps {
  label: string;
  value: string;
}

function MetricItem({ label, value }: MetricItemProps) {
  return (
    <div>
      <p className="text-[13px] font-medium text-[#8B95A5]">{label}</p>
      <p className="mt-1 text-[15px] font-semibold text-[#11131A] font-tabular">{value}</p>
    </div>
  );
}

export function ExplanationCard({ prediction }: ExplanationCardProps) {
  if (!prediction.explanation) {
    return null;
  }

  const e = prediction.explanation;

  return (
    <Card className="h-full">
      <CardContent className="space-y-5 h-full flex flex-col">
        <CardLabel>Technical Explanation</CardLabel>

        {/* Technical indicators grid */}
        <div className="grid grid-cols-2 gap-4 rounded-[12px] bg-[#F7F9FC] p-5 mt-2">
          <MetricItem label="Trend" value={e.trend} />
          <MetricItem label="Trend Strength" value={e.trendStrength} />
          <MetricItem label="RSI" value={e.rsi.toFixed(2)} />
          <MetricItem label="RSI State" value={e.rsiState} />
          <MetricItem label="ROC" value={e.roc.toFixed(2)} />
          <MetricItem label="Momentum" value={e.momentum.toFixed(2)} />
          <MetricItem label="ATR" value={e.atr.toFixed(2)} />
          <MetricItem label="Volatility" value={e.volatility.toFixed(6)} />
        </div>

        {/* Summary bullets */}
        {e.summary && e.summary.length > 0 && (
          <div className="border-t border-[#F0F4F8] pt-5 mt-auto">
            <p className="text-[13px] font-semibold text-[#8B95A5] mb-3 uppercase tracking-wide">Summary</p>
            <ul className="space-y-2.5">
              {e.summary.map((item, i) => (
                <li key={i} className="flex items-start gap-3 text-[15px] leading-relaxed text-[#5B6473]">
                  <span className="mt-2.5 h-1.5 w-1.5 shrink-0 rounded-full bg-[#0066FF]" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}