import { apiClient } from "./client";

class AnalyticsService {

  overview() {

    return apiClient.get(
      "/analytics/overview"
    );

  }

  confidence() {

    return apiClient.get(
      "/analytics/confidence"
    );

  }

  distribution() {

    return apiClient.get(
      "/analytics/distribution"
    );

  }

  recent() {

    return apiClient.get(
      "/analytics/recent"
    );

  }

}
export const analyticsService =
  new AnalyticsService();
  