import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import "@fontsource/plus-jakarta-sans";
import "@fontsource/space-grotesk";

import "./globals.css";

import Providers from "@/providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "Stock Price Trend Prediction",
    template: "%s | Stock Price Trend Prediction",
  },

  description:
    "Enterprise AI-powered stock trend prediction platform.",

  applicationName: "Stock Price Trend Prediction",

  authors: [
    {
      name: "Saurabh",
    },
  ],

  keywords: [
    "AI",
    "Stock Prediction",
    "Machine Learning",
    "Trading",
    "Analytics",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable}`}
    >
      <body className="bg-background text-foreground font-sans antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}