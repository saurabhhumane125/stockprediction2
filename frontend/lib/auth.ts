import { apiClient } from "@/lib/api/client";

export async function logout() {

  await apiClient.post(

    "/auth/logout"

  );

}

export async function currentUser() {

  const { data } = await apiClient.get(

    "/auth/me"

  );

  return data;

}