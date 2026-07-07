import "server-only";

import { redirect } from "next/navigation";

import { serverFetch } from "./api";

export interface SessionUser {

  id: number;

  full_name: string;

  email: string;

  is_active: number;

}

export async function getSession()

: Promise<SessionUser> {

  try {

    return await serverFetch<SessionUser>(
      "/auth/me",
    );

  }

  catch {

    redirect("/login");

  }

}