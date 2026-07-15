import { Activity, TrendingUp, TrendingDown, Clock, BrainCircuit } from "lucide-react";
import type { VisionResult } from "../hooks/useVisionPipeline";

export function VisionResultsPanel({ result }: { result: VisionResult }) {
  const isUp = result.prediction === "UP";

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Prediction Card */}
        <div className="p-6 rounded-xl border border-border bg-card flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <BrainCircuit className="w-5 h-5 text-primary" />
              AI Prediction
            </h3>
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${
              isUp ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'
            }`}>
              {result.prediction}
            </span>
          </div>
          <div className="flex items-end justify-between mt-auto">
            <div className="flex flex-col">
              <span className="text-sm text-muted-foreground">Confidence</span>
              <span className="text-3xl font-bold">{(result.confidence * 100).toFixed(1)}%</span>
            </div>
            {isUp ? (
              <TrendingUp className="w-12 h-12 text-green-500 opacity-80" />
            ) : (
              <TrendingDown className="w-12 h-12 text-red-500 opacity-80" />
            )}
          </div>
        </div>

        {/* Trace/Metadata Card */}
        <div className="p-6 rounded-xl border border-border bg-card flex flex-col justify-between">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold">Execution Trace</h3>
          </div>
          <div className="space-y-3 mt-auto">
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Session ID</span>
              <span className="font-mono text-xs">{result.trace.vision_session_id.substring(0, 8)}...</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Model Version</span>
              <span className="font-medium">{result.trace.model_version}</span>
            </div>
            <div className="flex justify-between items-center text-sm">
              <span className="text-muted-foreground">Inference Time</span>
              <span className="font-medium flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {result.trace.inference_latency_ms.toFixed(0)} ms
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
