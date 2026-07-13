import { apiClient } from "@/lib/api/client";

export async function apiRequest<T>(
  endpoint: string,
  options: {
    method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
    body?: unknown;
  } = {},
): Promise<T> {

  const response = await apiClient.request<T>({
    url: endpoint,
    method: options.method ?? "GET",
    data: options.body,
  });

  return response.data;

}