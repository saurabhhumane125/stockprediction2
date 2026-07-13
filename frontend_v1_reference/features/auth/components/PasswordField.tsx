"use client";

import { useState } from "react";
import { Lock, Eye, EyeOff } from "lucide-react";
import { Input } from "@/components/ui/Input";

interface Props {
  register: any;
  error?: string;
  id?: string;
  placeholder?: string;
}

export function PasswordField({
  register,
  error,
  id = "login-password",
  placeholder = "Enter your password",
}: Readonly<Props>) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <>
      <div className="relative">
        <div className="pointer-events-none absolute inset-y-0 left-4 flex items-center text-[#8B95A5]">
          <Lock size={18} strokeWidth={2.5} />
        </div>
        <Input
          id={id}
          type={showPassword ? "text" : "password"}
          placeholder={placeholder}
          className="!pl-[44px] !pr-12 !h-12 !rounded-[12px] !border-[#E8EDF2] focus:!border-[#0066FF] shadow-sm text-[15px]"
          {...register("password")}
        />
        <button
          type="button"
          onClick={() => setShowPassword(!showPassword)}
          className="absolute inset-y-0 right-4 flex items-center text-[#8B95A5] hover:text-[#5B6473] transition-colors"
          tabIndex={-1}
        >
          {showPassword ? <EyeOff size={18} strokeWidth={2.5} /> : <Eye size={18} strokeWidth={2.5} />}
        </button>
      </div>
      {error && (
        <p className="text-[13px] font-medium text-[#FF3B3B] mt-2">
          {error}
        </p>
      )}
    </>
  );
}