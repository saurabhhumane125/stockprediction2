import axios from "axios";

import {
  API_BASE_URL,
  REQUEST_TIMEOUT,
} from "@/lib/constants";

export const apiClient = axios.create({

  baseURL: API_BASE_URL,

  timeout: REQUEST_TIMEOUT,

  withCredentials: true,

  headers: {

    "Content-Type": "application/json",

  },

});

apiClient.interceptors.response.use(

  (response) => response,

  (error) => {

    if (

      error.response?.status === 401 &&

      typeof window !== "undefined"

    ) {

      window.location.href = "/login";

    }

    return Promise.reject(error);

  }

);