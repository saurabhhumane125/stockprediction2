import threading
import logging
from app.schemas import VisionMetricsResponse

logger = logging.getLogger(__name__)

class VisionMetricsService:
    """
    In-memory tracker for Vision Operations metrics.
    Uses threading.Lock for thread safety.
    """
    def __init__(self):
        self._lock = threading.Lock()
        
        self._success_count = 0
        self._failure_count = 0
        
        self._total_ocr_latency = 0.0
        self._total_feature_latency = 0.0
        self._total_inference_latency = 0.0
        self._total_request_latency = 0.0

    def record_success(self,
                       ocr_latency: float,
                       feature_latency: float,
                       inference_latency: float,
                       total_latency: float):
        with self._lock:
            self._success_count += 1
            self._total_ocr_latency += ocr_latency
            self._total_feature_latency += feature_latency
            self._total_inference_latency += inference_latency
            self._total_request_latency += total_latency
            
    def record_failure(self):
        with self._lock:
            self._failure_count += 1
            
    def get_metrics(self) -> VisionMetricsResponse:
        with self._lock:
            success = self._success_count
            failures = self._failure_count
            
            avg_ocr = (self._total_ocr_latency / success) if success > 0 else 0.0
            avg_feat = (self._total_feature_latency / success) if success > 0 else 0.0
            avg_inf = (self._total_inference_latency / success) if success > 0 else 0.0
            avg_tot = (self._total_request_latency / success) if success > 0 else 0.0
            
            return VisionMetricsResponse(
                success_count=success,
                failure_count=failures,
                avg_ocr_latency_ms=avg_ocr,
                avg_feature_generation_latency_ms=avg_feat,
                avg_inference_latency_ms=avg_inf,
                avg_total_request_latency_ms=avg_tot
            )
            
vision_metrics_service = VisionMetricsService()
