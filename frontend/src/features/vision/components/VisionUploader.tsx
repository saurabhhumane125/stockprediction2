"use client";

import { useState, useRef } from "react";
import { UploadCloud, Image as ImageIcon, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface VisionUploaderProps {
  onUpload: (file: File) => void;
  isLoading: boolean;
}

export function VisionUploader({ onUpload, isLoading }: VisionUploaderProps) {
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith("image/")) {
        onUpload(file);
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  return (
    <div
      className={`relative rounded-xl border-2 border-dashed p-12 transition-colors flex flex-col items-center justify-center text-center 
        ${dragActive ? "border-primary bg-primary/10" : "border-border bg-card hover:bg-accent/50"} 
        ${isLoading ? "opacity-50 pointer-events-none" : ""}`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        onChange={handleChange}
        className="hidden"
        aria-label="Upload chart image"
      />
      
      <div className="rounded-full bg-accent p-4 mb-4">
        <UploadCloud className="w-8 h-8 text-primary" />
      </div>
      
      <h3 className="text-xl font-semibold mb-2">Upload Chart Image</h3>
      <p className="text-muted-foreground mb-6 max-w-sm">
        Drag and drop your candlestick chart screenshot here, or click to browse.
      </p>
      
      <Button 
        onClick={() => inputRef.current?.click()}
        disabled={isLoading}
      >
        Select Image
      </Button>
    </div>
  );
}
