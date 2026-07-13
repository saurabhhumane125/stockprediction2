import { apiRequest } from "@/lib/api";
import type {
  AnalyticsOverview,
  PredictionDistribution,
  ConfidenceStatistics,
  RecentPrediction,
} from "../types/analytics.types";

export function getOverview() {
  return apiRequest<AnalyticsOverview>(
    "/analytics/overview",
  );
}

export function getDistribution() {
  return apiRequest<PredictionDistribution>(
    "/analytics/distribution",
  );
}

export function getConfidence() {
  return apiRequest<ConfidenceStatistics>(
    "/analytics/confidence",
  );
}

export function getRecent(
  limit = 20,
) {
  return apiRequest<RecentPrediction[]>(
    `/analytics/recent?limit=${limit}`,
  );
}