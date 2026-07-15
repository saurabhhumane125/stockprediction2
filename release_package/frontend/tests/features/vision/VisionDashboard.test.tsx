import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { VisionDashboard } from "../../../src/features/vision/components/VisionDashboard";
import { useVisionPipeline } from "../../../src/features/vision/hooks/useVisionPipeline";
import "@testing-library/jest-dom";

// Mock the hook
jest.mock("../../../src/features/vision/hooks/useVisionPipeline");

const mockUseVisionPipeline = useVisionPipeline as jest.Mock;

describe("VisionDashboard", () => {
  const defaultMockState = {
    state: "IDLE",
    result: null,
    error: null,
    previewUrl: null,
    processImage: jest.fn(),
    reset: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders uploader in IDLE state", () => {
    mockUseVisionPipeline.mockReturnValue(defaultMockState);
    render(<VisionDashboard />);
    expect(screen.getByText("Vision AI Analysis")).toBeInDocument();
    expect(screen.getByText(/Drag and drop your candlestick chart/i)).toBeInDocument();
    expect(screen.getByRole("button", { name: "Select Image" })).toBeInDocument();
  });

  it("renders timeline in PROCESSING state", () => {
    mockUseVisionPipeline.mockReturnValue({
      ...defaultMockState,
      state: "PROCESSING",
      previewUrl: "blob:http://localhost/test",
    });
    render(<VisionDashboard />);
    expect(screen.getByText("Processing Timeline")).toBeInDocument();
    expect(screen.getByText("Extracting Data (OCR)")).toBeInDocument();
  });

  it("renders error state correctly", () => {
    const errorMsg = "OCR Extraction failed: Invalid resolution";
    mockUseVisionPipeline.mockReturnValue({
      ...defaultMockState,
      state: "ERROR",
      error: errorMsg,
    });
    render(<VisionDashboard />);
    expect(screen.getByText("Processing Failed")).toBeInDocument();
    expect(screen.getByText(errorMsg)).toBeInDocument();
    expect(screen.getByRole("button", { name: /Try Again/i })).toBeInDocument();
  });

  it("renders results in COMPLETED state", () => {
    mockUseVisionPipeline.mockReturnValue({
      ...defaultMockState,
      state: "COMPLETED",
      result: {
        prediction: "UP",
        confidence: 0.95,
        trace: {
          vision_session_id: "test1234",
          model_version: "v1.0.0",
          inference_latency_ms: 150,
        },
      },
    });
    render(<VisionDashboard />);
    
    // Check prediction
    expect(screen.getByText("AI Prediction")).toBeInDocument();
    expect(screen.getByText("UP")).toBeInDocument();
    expect(screen.getByText("95.0%")).toBeInDocument();

    // Check trace
    expect(screen.getByText("Execution Trace")).toBeInDocument();
    expect(screen.getByText(/test1234/i)).toBeInDocument();
    expect(screen.getByText("v1.0.0")).toBeInDocument();
    expect(screen.getByText("150 ms")).toBeInDocument();

    // Check reset button
    expect(screen.getByRole("button", { name: /Analyze Another Chart/i })).toBeInDocument();
  });
});
