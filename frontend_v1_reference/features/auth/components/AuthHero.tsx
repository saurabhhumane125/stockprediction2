import { BrainCircuit, BarChart3, FileText, Users, TrendingUp, Shield, Zap } from "lucide-react";

export function AuthHero() {
  return (
    <div className="relative w-full h-full flex flex-col pb-16">
      
      {/* Top Accent */}
      <div className="w-12 h-1.5 rounded-full bg-gradient-to-r from-[#B4FF00] to-[#88CC00] mb-8 shadow-sm" />

      {/* Main Headline */}
      <h1 className="text-[52px] xl:text-[64px] font-bold leading-[1.05] tracking-tight font-[family-name:var(--font-space-grotesk)] mb-5">
        <span className="text-[#11131A]">Intelligent</span><br/>
        <span className="text-[#11131A]">Stock </span>
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#0066FF] via-[#4D94FF] to-[#91CC00]">Predictions.</span>
      </h1>

      <p className="text-[16px] xl:text-[18px] text-[#5B6473] font-medium leading-relaxed max-w-[480px] mb-12">
        AI-powered market intelligence and predictive analytics<br/>
        for smarter investment decisions.
      </p>

      {/* Features List */}
      <div className="flex flex-col gap-8 relative z-20">
        
        {/* Feature 1 */}
        <div className="flex gap-5 items-start">
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-[14px] bg-white/60 backdrop-blur-sm shadow-[0_8px_24px_rgba(0,102,255,0.06)] border border-white text-[#0066FF]">
            <BrainCircuit size={24} strokeWidth={2} />
          </div>
          <div className="pt-1">
            <h3 className="text-[16px] font-bold text-[#11131A] mb-1">AI-Powered Predictions</h3>
            <p className="text-[14px] text-[#5B6473] max-w-[300px] leading-relaxed">Advanced machine learning models trained on historical market data.</p>
          </div>
        </div>

        {/* Feature 2 */}
        <div className="flex gap-5 items-start">
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-[14px] bg-white/60 backdrop-blur-sm shadow-[0_8px_24px_rgba(153,204,0,0.08)] border border-white text-[#88CC00]">
            <BarChart3 size={24} strokeWidth={2} />
          </div>
          <div className="pt-1">
            <h3 className="text-[16px] font-bold text-[#11131A] mb-1">Technical Analysis</h3>
            <p className="text-[14px] text-[#5B6473] max-w-[300px] leading-relaxed">20+ technical indicators, chart patterns and market analytics.</p>
          </div>
        </div>

        {/* Feature 3 */}
        <div className="flex gap-5 items-start">
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-[14px] bg-white/60 backdrop-blur-sm shadow-[0_8px_24px_rgba(138,43,226,0.06)] border border-white text-[#9C27B0]">
            <FileText size={24} strokeWidth={2} />
          </div>
          <div className="pt-1">
            <h3 className="text-[16px] font-bold text-[#11131A] mb-1">Real-time Insights</h3>
            <p className="text-[14px] text-[#5B6473] max-w-[300px] leading-relaxed">Live market data, sentiment analysis and actionable recommendations.</p>
          </div>
        </div>

      </div>

      {/* =========================================
          FLOATING GRAPHICS SECTION 
          ========================================= */}
      
      {/* Container for absolute graphics, pushed strictly between left and right */}
      <div className="hidden lg:block absolute top-[-40px] left-[350px] xl:left-[450px] w-[500px] bottom-0 pointer-events-none z-10">
        
        {/* Massive Background Candlestick Curve with blend mode */}
        <div className="absolute top-[80px] left-[0px] w-[600px] h-[450px] opacity-80 mix-blend-multiply">
          <svg width="100%" height="100%" viewBox="0 0 600 450" fill="none">
            {/* Smooth glowing curve */}
            <path d="M 0 400 C 200 400, 300 250, 450 150 C 520 80, 570 50, 600 20" stroke="url(#bigChartLine)" strokeWidth="6" strokeLinecap="round" filter="drop-shadow(0 10px 15px rgba(0,102,255,0.2))" />
            
            {/* Candlesticks placed along the curve */}
            <g opacity="0.9">
              {/* Blue/Red/Green candles */}
              <rect x="50" y="380" width="8" height="30" rx="2" fill="#0066FF" opacity="0.4" />
              <line x1="54" y1="370" x2="54" y2="420" stroke="#0066FF" strokeWidth="2" opacity="0.4" />
              
              <rect x="100" y="360" width="8" height="20" rx="2" fill="#0066FF" opacity="0.5" />
              <line x1="104" y1="350" x2="104" y2="390" stroke="#0066FF" strokeWidth="2" opacity="0.5" />

              <rect x="150" y="320" width="8" height="40" rx="2" fill="#0066FF" opacity="0.6" />
              <line x1="154" y1="310" x2="154" y2="370" stroke="#0066FF" strokeWidth="2" opacity="0.6" />

              <rect x="200" y="290" width="8" height="25" rx="2" fill="#0066FF" opacity="0.7" />
              <line x1="204" y1="280" x2="204" y2="325" stroke="#0066FF" strokeWidth="2" opacity="0.7" />

              <rect x="250" y="250" width="8" height="35" rx="2" fill="#4D94FF" opacity="0.8"/>
              <line x1="254" y1="230" x2="254" y2="295" stroke="#4D94FF" strokeWidth="2" opacity="0.8"/>

              <rect x="300" y="210" width="8" height="45" rx="2" fill="#4D94FF" />
              <line x1="304" y1="190" x2="304" y2="265" stroke="#4D94FF" strokeWidth="2" />

              <rect x="350" y="190" width="8" height="20" rx="2" fill="#88CC00" opacity="0.8" />
              <line x1="354" y1="180" x2="354" y2="220" stroke="#88CC00" strokeWidth="2" opacity="0.8" />

              <rect x="400" y="150" width="8" height="55" rx="2" fill="#88CC00" />
              <line x1="404" y1="130" x2="404" y2="215" stroke="#88CC00" strokeWidth="2" />

              <rect x="450" y="120" width="8" height="40" rx="2" fill="#B4FF00" />
              <line x1="454" y1="100" x2="454" y2="170" stroke="#B4FF00" strokeWidth="2" />

              <rect x="500" y="100" width="8" height="25" rx="2" fill="#0066FF" opacity="0.5"/>
              <line x1="504" y1="80" x2="504" y2="135" stroke="#0066FF" strokeWidth="2" opacity="0.5"/>

              <rect x="550" y="50" width="8" height="65" rx="2" fill="#B4FF00" />
              <line x1="554" y1="30" x2="554" y2="125" stroke="#B4FF00" strokeWidth="2" />
            </g>

            <defs>
              <linearGradient id="bigChartLine" x1="0" y1="400" x2="600" y2="20" gradientUnits="userSpaceOnUse">
                <stop stopColor="#0066FF" stopOpacity="0.1" />
                <stop offset="0.4" stopColor="#0066FF" stopOpacity="0.8" />
                <stop offset="1" stopColor="#B4FF00" stopOpacity="1" />
              </linearGradient>
            </defs>
          </svg>
        </div>

        {/* NIFTY 50 Card */}
        <div className="absolute left-[150px] top-[10px] bg-white/70 backdrop-blur-xl border border-white/60 shadow-[0_16px_40px_rgba(0,102,255,0.05)] rounded-[16px] px-5 py-4 z-30">
          <p className="text-[11px] text-[#8B95A5] font-bold mb-1 uppercase tracking-wider">NIFTY 50</p>
          <p className="text-[18px] font-bold text-[#11131A] font-tabular">24,752.45</p>
          <p className="text-[13px] font-bold text-[#88CC00] flex items-center gap-1 mt-1">
            +1.28% <TrendingUp size={14} strokeWidth={2.5} />
          </p>
        </div>

        {/* AI Prediction Chart Card */}
        <div className="absolute left-[20px] top-[240px] bg-white/50 backdrop-blur-2xl border border-white/60 rounded-[24px] shadow-[0_32px_64px_rgba(0,102,255,0.08)] p-6 w-[440px] z-20">
          <div className="flex justify-between items-center mb-6">
            <h4 className="text-[15px] font-bold text-[#11131A]">AI Prediction <span className="text-[#8B95A5] font-normal">(Next 7 Days)</span></h4>
          </div>
          
          <div className="relative h-[160px] w-full">
            {/* Chart Graphic SVG */}
            <svg width="100%" height="100%" viewBox="0 0 380 160" preserveAspectRatio="none">
              {/* Y Axis lines */}
              <line x1="0" y1="20" x2="380" y2="20" stroke="#E8EDF2" strokeWidth="1" strokeDasharray="4 4" />
              <line x1="0" y1="70" x2="380" y2="70" stroke="#E8EDF2" strokeWidth="1" strokeDasharray="4 4" />
              <line x1="0" y1="120" x2="380" y2="120" stroke="#E8EDF2" strokeWidth="1" strokeDasharray="4 4" />
              
              {/* Historical Line (Blue) */}
              <path d="M 0 140 L 40 120 L 80 130 L 120 90 L 160 100 L 200 80" stroke="#0066FF" strokeWidth="3" fill="none" strokeLinejoin="round" />
              <circle cx="40" cy="120" r="4" fill="#0066FF" />
              <circle cx="80" cy="130" r="4" fill="#0066FF" />
              <circle cx="120" cy="90" r="4" fill="#0066FF" />
              <circle cx="160" cy="100" r="4" fill="#0066FF" />
              <circle cx="200" cy="80" r="5" fill="#0066FF" stroke="white" strokeWidth="2" />

              {/* Area under historical */}
              <path d="M 0 140 L 40 120 L 80 130 L 120 90 L 160 100 L 200 80 L 200 160 L 0 160 Z" fill="url(#histArea)" />

              {/* Prediction Line (Green) */}
              <path d="M 200 80 L 240 60 L 280 70 L 320 30 L 360 40 L 380 20" stroke="#88CC00" strokeWidth="3" strokeDasharray="6 4" fill="none" strokeLinejoin="round" />
              <circle cx="240" cy="60" r="4" fill="#88CC00" />
              <circle cx="280" cy="70" r="4" fill="#88CC00" />
              <circle cx="320" cy="30" r="4" fill="#88CC00" />
              <circle cx="360" cy="40" r="4" fill="#88CC00" />
              <circle cx="380" cy="20" r="5" fill="#88CC00" stroke="white" strokeWidth="2" />

              {/* Area under prediction */}
              <path d="M 200 80 L 240 60 L 280 70 L 320 30 L 360 40 L 380 20 L 380 160 L 200 160 Z" fill="url(#predArea)" />

              <defs>
                <linearGradient id="histArea" x1="0" y1="80" x2="0" y2="160" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#0066FF" stopOpacity="0.2" />
                  <stop offset="1" stopColor="#0066FF" stopOpacity="0" />
                </linearGradient>
                <linearGradient id="predArea" x1="0" y1="20" x2="0" y2="160" gradientUnits="userSpaceOnUse">
                  <stop stopColor="#88CC00" stopOpacity="0.25" />
                  <stop offset="1" stopColor="#88CC00" stopOpacity="0" />
                </linearGradient>
              </defs>
            </svg>

            {/* Growth Text Overlay */}
            <div className="absolute right-0 bottom-4 text-right">
              <p className="text-[24px] font-bold text-[#88CC00] font-tabular">+4.28%</p>
              <p className="text-[12px] text-[#5B6473] font-medium">Predicted Growth</p>
            </div>
          </div>
          
          {/* X axis labels */}
          <div className="flex justify-between text-[11px] font-medium text-[#8B95A5] mt-3">
            <span>May 2</span><span>May 3</span><span>May 4</span><span>May 5</span><span>May 6</span><span>May 7</span><span>May 8</span>
          </div>
        </div>

      </div>

      {/* Stats Bottom Card (Moved out of absolute so it naturally flows below features, avoiding footer overlapping) */}
      <div className="hidden lg:flex mt-12 bg-white/60 backdrop-blur-xl border border-white/60 shadow-[0_16px_40px_rgba(0,102,255,0.04)] rounded-[20px] px-8 py-6 items-center justify-between gap-10 xl:gap-14 w-max relative z-30">
        <div className="text-center flex flex-col items-center">
          <div className="flex justify-center mb-2 text-[#0066FF]"><Users size={20}/></div>
          <p className="text-[22px] font-bold text-[#11131A] font-[family-name:var(--font-space-grotesk)]">10K+</p>
          <p className="text-[12px] text-[#5B6473] font-medium mt-1">Active Users</p>
        </div>
        <div className="w-px h-12 bg-[#D7DEE7]" />
        <div className="text-center flex flex-col items-center">
          <div className="flex justify-center mb-2 text-[#0066FF]"><TrendingUp size={20}/></div>
          <p className="text-[22px] font-bold text-[#11131A] font-[family-name:var(--font-space-grotesk)]">95%+</p>
          <p className="text-[12px] text-[#5B6473] font-medium mt-1">Model Accuracy</p>
        </div>
        <div className="w-px h-12 bg-[#D7DEE7]" />
        <div className="text-center flex flex-col items-center">
          <div className="flex justify-center mb-2 text-[#0066FF]"><Shield size={20}/></div>
          <p className="text-[22px] font-bold text-[#11131A] font-[family-name:var(--font-space-grotesk)]">256-bit</p>
          <p className="text-[12px] text-[#5B6473] font-medium mt-1">Bank-level Security</p>
        </div>
        <div className="w-px h-12 bg-[#D7DEE7]" />
        <div className="text-center flex flex-col items-center">
          <div className="flex justify-center mb-2 text-[#11131A]"><Zap size={20}/></div>
          <p className="text-[22px] font-bold text-[#11131A] font-[family-name:var(--font-space-grotesk)]">Live</p>
          <p className="text-[12px] text-[#5B6473] font-medium mt-1">Market Updates</p>
        </div>
      </div>

    </div>
  );
}