import type { Metadata } from "next";
import { Space_Grotesk, Plus_Jakarta_Sans } from "next/font/google";

import "./globals.css";

import Providers from "@/providers";

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
});

const plusJakartaSans = Plus_Jakarta_Sans({
  variable: "--font-plus-jakarta-sans",
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
      className={`${spaceGrotesk.variable} ${plusJakartaSans.variable}`}
    >
      <body className="bg-background text-foreground font-sans antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}