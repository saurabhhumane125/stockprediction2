import type { ReactNode } from "react";
import { TrendingUp, Shield } from "lucide-react";

interface Props {
  hero: ReactNode;
  children: ReactNode;
}

export function AuthLayout({ hero, children }: Props) {
  return (
    <main className="min-h-screen w-full flex bg-[#F6F8FB] relative overflow-hidden font-sans">
      
      {/* Background Abstract Waves */}
      <div className="absolute inset-0 pointer-events-none z-0 opacity-70">
        <svg className="w-full h-full object-cover" viewBox="0 0 1440 900" fill="none" preserveAspectRatio="xMidYMid slice">
          {/* Subtle glowing orbs */}
          <circle cx="200" cy="800" r="400" fill="#0066FF" opacity="0.04" filter="blur(80px)" />
          <circle cx="1200" cy="200" r="300" fill="#B4FF00" opacity="0.04" filter="blur(60px)" />
          <circle cx="800" cy="800" r="300" fill="#B4FF00" opacity="0.03" filter="blur(60px)" />

          {/* Complex intersecting thin lines representing market waves */}
          <path d="M-100 400 C 200 500, 400 800, 800 700 C 1200 600, 1400 300, 1600 200" stroke="url(#waveGrad1)" strokeWidth="1" opacity="0.5" fill="none" />
          <path d="M-100 420 C 300 550, 500 850, 900 750 C 1300 650, 1450 350, 1600 250" stroke="url(#waveGrad2)" strokeWidth="0.5" opacity="0.6" fill="none" />
          <path d="M-100 440 C 250 520, 450 780, 850 680 C 1250 580, 1350 320, 1600 220" stroke="url(#waveGrad1)" strokeWidth="0.5" opacity="0.4" fill="none" />
          <path d="M-100 600 C 300 600, 600 900, 1000 800 C 1400 700, 1500 400, 1600 300" stroke="url(#waveGrad2)" strokeWidth="1" opacity="0.3" fill="none" />
          <path d="M-100 620 C 350 650, 650 950, 1050 850 C 1450 750, 1550 450, 1600 350" stroke="url(#waveGrad1)" strokeWidth="0.5" opacity="0.5" fill="none" />
          
          <path d="M-100 700 C 200 800, 400 950, 800 900 C 1200 850, 1400 600, 1600 500" stroke="url(#waveGrad3)" strokeWidth="0.5" opacity="0.6" fill="none" />

          {/* Additional sweeping curves */}
          <path d="M0 800 C 400 850, 600 700, 1000 600 C 1300 500, 1400 200, 1500 0" stroke="url(#waveGrad1)" strokeWidth="1" opacity="0.2" fill="none" />
          <path d="M0 820 C 450 870, 650 720, 1050 620 C 1350 520, 1450 220, 1500 20" stroke="url(#waveGrad2)" strokeWidth="0.5" opacity="0.3" fill="none" />

          <defs>
            <linearGradient id="waveGrad1" x1="0" y1="0" x2="1440" y2="900" gradientUnits="userSpaceOnUse">
              <stop stopColor="#0066FF" stopOpacity="0.8" />
              <stop offset="0.5" stopColor="#0066FF" stopOpacity="0.2" />
              <stop offset="1" stopColor="#B4FF00" stopOpacity="0.6" />
            </linearGradient>
            <linearGradient id="waveGrad2" x1="0" y1="900" x2="1440" y2="0" gradientUnits="userSpaceOnUse">
              <stop stopColor="#B4FF00" stopOpacity="0.5" />
              <stop offset="0.5" stopColor="#0066FF" stopOpacity="0.1" />
              <stop offset="1" stopColor="#0066FF" stopOpacity="0.8" />
            </linearGradient>
            <linearGradient id="waveGrad3" x1="0" y1="450" x2="1440" y2="450" gradientUnits="userSpaceOnUse">
              <stop stopColor="#4D94FF" stopOpacity="0.6" />
              <stop offset="0.5" stopColor="#B4FF00" stopOpacity="0.2" />
              <stop offset="1" stopColor="#B4FF00" stopOpacity="0.7" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      {/* Top Bar */}
      <nav className="absolute top-0 left-0 w-full flex justify-between items-start px-8 lg:px-16 py-8 z-30 pointer-events-none">
        {/* Logo */}
        <div className="flex items-center gap-3.5 pointer-events-auto">
          <div className="flex h-[42px] w-[42px] items-center justify-center rounded-[10px] bg-[#0066FF] shadow-lg shadow-blue-500/20">
            <TrendingUp size={22} className="text-white" strokeWidth={2.5} />
          </div>
          <div>
            <h1 className="text-[19px] font-bold text-[#11131A] font-[family-name:var(--font-space-grotesk)] leading-tight tracking-tight">STPTS</h1>
            <p className="text-[11px] text-[#5B6473] font-medium tracking-wide">Stock Price Trend Prediction System</p>
          </div>
        </div>

        {/* Security Badge */}
        <div className="hidden md:flex items-center gap-3 pointer-events-auto bg-white/50 backdrop-blur-md border border-white/60 px-5 py-2.5 rounded-full shadow-sm">
          <Shield size={18} className="text-[#0066FF]" strokeWidth={2.5} />
          <div>
            <p className="text-[12px] font-bold text-[#11131A] leading-tight">Bank-level security</p>
            <p className="text-[11px] text-[#5B6473] font-medium leading-tight mt-0.5">Your data is encrypted</p>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <div className="relative z-10 flex flex-col lg:flex-row justify-between w-full max-w-[1800px] mx-auto pt-32 pb-24 px-8 lg:px-16 xl:px-24 min-h-screen">
        
        {/* Left Side: Hero */}
        <section className="flex-1 flex flex-col relative z-20">
          {hero}
        </section>

        {/* Right Side: Form */}
        <section className="w-full lg:w-[480px] xl:w-[500px] shrink-0 flex items-center justify-end relative z-30 mt-12 lg:mt-0">
          <div className="w-full bg-white/80 backdrop-blur-2xl rounded-[24px] shadow-[0_32px_80px_rgba(0,102,255,0.06),0_4px_24px_rgba(0,0,0,0.02)] border border-white p-8 lg:p-12 animate-page-enter relative overflow-hidden">
            {/* Subtle glow behind card content */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-[#0066FF]/[0.03] blur-3xl rounded-full -z-10 pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-[#B4FF00]/[0.04] blur-3xl rounded-full -z-10 pointer-events-none" />
            {children}
          </div>
        </section>
      </div>

      {/* Footer */}
      <footer className="absolute bottom-0 left-0 w-full flex flex-col md:flex-row justify-between items-center px-8 lg:px-16 py-8 z-30 pointer-events-none">
        <p className="text-[12px] text-[#8B95A5] font-medium pointer-events-auto">
          © 2026 Stock Price Trend Prediction System. All rights reserved.
        </p>
        <div className="flex items-center gap-6 mt-4 md:mt-0 pointer-events-auto">
          <a href="#" className="text-[12px] font-semibold text-[#5B6473] hover:text-[#11131A] transition-colors">Privacy Policy</a>
          <div className="w-px h-3 bg-[#D7DEE7]" />
          <a href="#" className="text-[12px] font-semibold text-[#5B6473] hover:text-[#11131A] transition-colors">Terms of Service</a>
          <div className="w-px h-3 bg-[#D7DEE7]" />
          <a href="#" className="text-[12px] font-semibold text-[#5B6473] hover:text-[#11131A] transition-colors">Help Center</a>
        </div>
      </footer>
    </main>
  );
}