import { ReactNode } from "react"
import { TrendingUp } from "lucide-react"

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen grid grid-cols-1 md:grid-cols-2 bg-background">
      {/* Left Panel - Branding/Visual */}
      <div className="hidden md:flex flex-col bg-zinc-950 text-white justify-between p-12 relative overflow-hidden">
        {/* Abstract background effects */}
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-zinc-900 to-zinc-950 pointer-events-none" />
        <div className="absolute -bottom-[20%] -left-[20%] w-[140%] h-[60%] bg-zinc-800 rounded-[100%] blur-3xl pointer-events-none opacity-50" />

        <div className="relative z-10 flex items-center gap-2">
          <TrendingUp className="w-8 h-8 text-white" />
          <span className="text-xl font-bold tracking-tight">TradePredict</span>
        </div>
        
        <div className="relative z-10 space-y-6 max-w-lg">
          <h1 className="text-4xl font-semibold tracking-tight text-white">
            Precision insights for the modern trader.
          </h1>
          <p className="text-lg text-zinc-400">
            Leverage enterprise-grade AI to forecast market trends, analyze risk, and optimize your portfolio strategy in real-time.
          </p>
        </div>

        <div className="relative z-10 flex items-center gap-4 text-sm text-zinc-400 font-medium">
          <span>Enterprise Grade</span>
          <span className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
          <span>Real-time Analytics</span>
          <span className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
          <span>AI Powered</span>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex items-center justify-center p-8 bg-background relative">
        <div className="w-full max-w-[400px]">
          {children}
        </div>
      </div>
    </div>
  )
}
