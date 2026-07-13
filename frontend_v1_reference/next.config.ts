import type { NextConfig } from "next";

const nextConfig: NextConfig = {

  reactStrictMode: true,

  poweredByHeader: false,

  compress: true,

  experimental: {

    optimizePackageImports: [

      "lucide-react",

      "framer-motion",

    ],

  },

  allowedDevOrigins: [
    "localhost",
    "172.20.80.1",
  ],

};

export default nextConfig;