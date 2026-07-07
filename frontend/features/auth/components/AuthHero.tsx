import {
  ArrowUpRight,
  BarChart3,
  BrainCircuit,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";

import { APP } from "@/lib/app";

export function AuthHero() {

  return (

    <section
      className="
        relative
        flex
        min-h-[820px]
        flex-col
        justify-between
      "
    >

      {/* Decorative Blobs */}

      <div
        className="
          absolute
          left-0
          top-0
          h-72
          w-72
          rounded-full
          bg-[#0066FF]/10
          blur-[120px]
        "
      />

      <div
        className="
          absolute
          right-24
          bottom-24
          h-64
          w-64
          rounded-full
          bg-[#B4FF00]/20
          blur-[120px]
        "
      />

      {/* Header */}

      <div className="relative z-10">

        <div
          className="
            flex
            h-20
            w-20
            items-center
            justify-center
            rounded-[28px]
            bg-[#0066FF]
            shadow-xl
          "
        >

          <TrendingUp
            size={42}
            className="text-white"
          />

        </div>

        <p
          className="
            mt-10
            text-sm
            font-semibold
            uppercase
            tracking-[0.25em]
            text-[#0066FF]
          "
        >

          Stock Prediction Platform

        </p>

        <h1
          className="
            mt-5
            max-w-2xl
            font-['Space_Grotesk']
            text-7xl
            font-bold
            leading-[1.02]
            text-[#11131A]
          "
        >

          Predict Tomorrow's

          <br />

          Market Direction

        </h1>

        <p
          className="
            mt-8
            max-w-2xl
            text-xl
            leading-9
            text-[#5B6473]
          "
        >

          {APP.tagline}

        </p>

      </div>

      {/* Floating Cards */}

      <div
        className="
          relative
          z-10
          mt-16
          grid
          grid-cols-3
          gap-6
        "
      >

        <div
          className="
            rounded-[30px]
            bg-white
            p-7
            shadow-xl
          "
        >

          <BrainCircuit
            className="text-[#0066FF]"
            size={30}
          />

          <h3
            className="
              mt-6
              font-['Space_Grotesk']
              text-2xl
              font-bold
            "
          >

            AI Prediction

          </h3>

          <p
            className="
              mt-3
              leading-7
              text-[#5B6473]
            "
          >

            Deep-learning powered stock trend forecasting using GRU models.

          </p>

        </div>

        <div
          className="
            rounded-[30px]
            bg-white
            p-7
            shadow-xl
          "
        >

          <BarChart3
            className="text-[#0066FF]"
            size={30}
          />

          <h3
            className="
              mt-6
              font-['Space_Grotesk']
              text-2xl
              font-bold
            "
          >

            Technical Signals

          </h3>

          <p
            className="
              mt-3
              leading-7
              text-[#5B6473]
            "
          >

            RSI, EMA, ATR, MACD, ADX and multiple technical indicators.

          </p>

        </div>

        <div
          className="
            rounded-[30px]
            bg-white
            p-7
            shadow-xl
          "
        >

          <ShieldCheck
            className="text-[#0066FF]"
            size={30}
          />

          <h3
            className="
              mt-6
              font-['Space_Grotesk']
              text-2xl
              font-bold
            "
          >

            Decision Support

          </h3>

          <p
            className="
              mt-3
              leading-7
              text-[#5B6473]
            "
          >

            Confidence scores, explanations and market regime analysis.

          </p>

        </div>

      </div>

      {/* Bottom Card */}

      <div
        className="
          relative
          z-10
          mt-16
          flex
          items-center
          justify-between
          rounded-[34px]
          bg-[#11131A]
          px-10
          py-9
          text-white
          shadow-2xl
        "
      >

        <div>

          <p
            className="
              text-base
              text-gray-300
            "
          >

            Average Model Accuracy

          </p>

          <h2
            className="
              mt-3
              font-['Space_Grotesk']
              text-6xl
              font-bold
            "
          >

            92.4%

          </h2>

        </div>

        <div
          className="
            flex
            h-20
            w-20
            items-center
            justify-center
            rounded-3xl
            bg-[#B4FF00]
          "
        >

          <ArrowUpRight
            size={34}
            className="text-[#11131A]"
          />

        </div>

      </div>

    </section>

  );

}