import * as api from "../api/analytics.api";

export const analyticsService = {

  getOverview: api.getOverview,

  getDistribution: api.getDistribution,

  getConfidence: api.getConfidence,

  getRecent: api.getRecent,

};