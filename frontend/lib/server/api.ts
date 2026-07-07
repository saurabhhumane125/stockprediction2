import "server-only";

import { cookies } from "next/headers";

import { API_BASE_URL } from "@/lib/constants";

export async function serverFetch<T>(

  endpoint: string,

  options: RequestInit = {},

): Promise<T> {

  const cookieStore = await cookies();

  const response = await fetch(

    `${API_BASE_URL}${endpoint}`,

    {

      ...options,

      headers: {

        Cookie: cookieStore.toString(),

        ...(options.headers ?? {}),

      },

      cache: "no-store",

    },

  );

  if (!response.ok) {

    throw new Error(

      `Request failed: ${response.status}`,

    );

  }

  return response.json();

}