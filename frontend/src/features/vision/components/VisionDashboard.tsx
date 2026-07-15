"use client";

import { useVisionPipeline } from "../hooks/useVisionPipeline";
import { VisionUploader } from "./VisionUploader";
import { ProcessingTimeline } from "./ProcessingTimeline";
import { VisionResultsPanel } from "./VisionResultsPanel";
import { Button } from "@/components/ui/button";
import { RefreshCcw } from "lucide-react";
import Image from "next/image";

export function VisionDashboard() {
  const { state, result, error, previewUrl, processImage, reset } = useVisionPipeline();

  const handleUpload = (file: File) => {
    processImage(file);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Vision AI Analysis</h1>
        <p className="text-muted-foreground mt-2">
          Upload a candlestick chart screenshot to instantly generate an AI-driven trend prediction.
        </p>
      </div>

      {state === 'IDLE' ? (
        <VisionUploader onUpload={handleUpload} isLoading={false} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-6">
            {previewUrl && (
              <div className="relative aspect-video rounded-xl overflow-hidden border border-border bg-black/5">
                <Image 
                  src={previewUrl} 
                  alt="Chart Preview" 
                  fill 
                  className="object-contain" 
                  unoptimized // Local blob URL
                />
              </div>
            )}
            
            {(state === 'UPLOADING' || state === 'PROCESSING') && (
              <ProcessingTimeline state={state} />
            )}

            {state === 'ERROR' && (
              <div className="p-6 bg-red-500/10 border border-red-500/20 rounded-xl text-red-500">
                <h3 className="font-semibold mb-2">Processing Failed</h3>
                <p className="text-sm opacity-90">{error}</p>
                <Button variant="outline" onClick={reset} className="mt-4 text-foreground">
                  <RefreshCcw className="w-4 h-4 mr-2" /> Try Again
                </Button>
              </div>
            )}
          </div>

          <div>
            {state === 'COMPLETED' && result && (
              <div className="space-y-6">
                <VisionResultsPanel result={result} />
                <Button variant="outline" onClick={reset} className="w-full">
                  <RefreshCcw className="w-4 h-4 mr-2" /> Analyze Another Chart
                </Button>
              </div>
            )}
            
            {state !== 'COMPLETED' && state !== 'ERROR' && (
              <div className="h-full flex items-center justify-center p-12 border-2 border-dashed border-border rounded-xl opacity-50">
                <p className="text-center text-sm text-muted-foreground">
                  Awaiting analysis results...
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
