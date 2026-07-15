import { api } from "./index"

export const authApi = {
  login: async (credentials: Record<string, string>) => {
    // Usually OAuth2 password flow expects form data, let's see how frontend_v1_reference does it
    // Wait, the prompt says POST /auth/login. I'll send it as JSON first, but if the backend uses FastAPI OAuth2PasswordRequestForm it needs application/x-www-form-urlencoded
    const response = await api.post("/auth/login", credentials)
    return response.data
  },
  register: async (data: Record<string, string>) => {
    const response = await api.post("/auth/register", data)
    return response.data
  },
  logout: async () => {
    const response = await api.post("/auth/logout")
    return response.data
  },
  me: async () => {
    const response = await api.get("/auth/me")
    return response.data
  },
  getMe: async () => {
    const response = await api.get("/auth/me")
    return response.data
  },
}
