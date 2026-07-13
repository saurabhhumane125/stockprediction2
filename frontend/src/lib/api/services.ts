import { api } from "./index"

export const stocksApi = {
  getStocks: async () => {
    const response = await api.get("/stocks/")
    return response.data
  },
  getStock: async (symbol: string) => {
    const response = await api.get(`/stocks/${symbol}`)
    return response.data
  },
}

export const predictionApi = {
  predict: async (data: { stock: string; features: number[][] }) => {
    const response = await api.post("/predict", data)
    return response.data
  },
  predictLive: async (stock: string) => {
    const response = await api.post(`/predict/live/${stock}`)
    return response.data
  }
}

export const analyticsApi = {
  getOverview: async () => {
    const response = await api.get("/analytics/overview")
    return response.data
  },
  getRecent: async () => {
    const response = await api.get("/analytics/recent")
    return response.data
  },
  getDistribution: async () => {
    const response = await api.get("/analytics/distribution")
    return response.data
  },
  getConfidence: async () => {
    const response = await api.get("/analytics/confidence")
    return response.data
  },
  getAccuracy: async (symbol: string) => {
    const response = await api.get(`/analytics/accuracy/${symbol}`)
    return response.data
  }
}

export const historyApi = {
  getHistory: async () => {
    const response = await api.get("/history/")
    return response.data
  },
  getHistoryBySymbol: async (symbol: string) => {
    const response = await api.get(`/history/${symbol}`)
    return response.data
  },
  getLatestBySymbol: async (symbol: string) => {
    const response = await api.get(`/history/latest/${symbol}`)
    return response.data
  }
}

export const backtestingApi = {
  getBacktesting: async (symbol: string) => {
    const response = await api.get(`/backtesting/${symbol}`)
    return response.data
  }
}
