"use client";

import { Mail, Lock, Eye, EyeOff, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { PasswordField } from "./PasswordField";
import { useLogin } from "../hooks/useLogin";

export function LoginForm() {
  const {
    register,
    handleSubmit,
    onSubmit,
    errors,
    loading,
  } = useLogin();

  return (
    <div className="w-full flex flex-col">
      {/* Heading */}
      <div className="mb-10 text-center md:text-left">
        <h2 className="text-[32px] font-bold text-[#11131A] font-[family-name:var(--font-space-grotesk)] tracking-tight leading-tight">
          Welcome back
        </h2>
        <p className="text-[#5B6473] text-[15px] font-medium mt-2">
          Sign in to your account to continue
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="w-full flex flex-col" noValidate>
        {/* Email */}
        <div className="mb-6">
          <label
            htmlFor="login-email"
            className="block text-[14px] font-bold text-[#11131A] mb-2.5"
          >
            Email address
          </label>
          <div className="relative">
            <div className="pointer-events-none absolute inset-y-0 left-4 flex items-center text-[#8B95A5]">
              <Mail size={18} strokeWidth={2.5} />
            </div>
            <Input
              id="login-email"
              type="email"
              placeholder="name@example.com"
              className="!pl-[44px] !h-12 !rounded-[12px] !border-[#E8EDF2] focus:!border-[#0066FF] shadow-sm text-[15px]"
              {...register("email")}
            />
          </div>
          {errors.email && (
            <p className="text-[13px] font-medium text-[#FF3B3B] mt-2">
              {errors.email.message}
            </p>
          )}
        </div>

        {/* Password */}
        <div className="mb-6">
          <label
            htmlFor="login-password"
            className="block text-[14px] font-bold text-[#11131A] mb-2.5"
          >
            Password
          </label>
          <PasswordField
            register={register}
            error={errors.password?.message}
          />
        </div>

        {/* Options */}
        <div className="flex items-center justify-between mb-10">
          <label className="flex items-center gap-3 cursor-pointer group">
            <div className="relative flex items-center justify-center h-[22px] w-[22px]">
              <input
                type="checkbox"
                className="peer appearance-none h-[22px] w-[22px] rounded-[6px] border-[1.5px] border-[#D7DEE7] bg-white checked:bg-[#0066FF] checked:border-[#0066FF] cursor-pointer transition-all shadow-sm"
              />
              <svg className="absolute inset-0 m-auto w-3.5 h-3.5 text-white pointer-events-none opacity-0 peer-checked:opacity-100 transition-opacity" viewBox="0 0 14 10" fill="none">
                <path d="M1 5L5 9L13 1" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <span className="text-[14px] text-[#5B6473] font-medium select-none group-hover:text-[#11131A] transition-colors">
              Remember me
            </span>
          </label>
          <a href="#" className="text-[14px] font-bold text-[#0066FF] hover:text-[#0055D4] transition-colors">
            Forgot password?
          </a>
        </div>

        {/* Submit */}
        <div className="mb-10">
          <Button
            type="submit"
            loading={loading}
            size="lg"
            className="w-full h-[52px] text-[16px] font-bold rounded-[12px] flex items-center justify-center gap-2 group"
          >
            Sign in
            <ArrowRight size={18} strokeWidth={2.5} className="group-hover:translate-x-1 transition-transform" />
          </Button>
        </div>
      </form>

      {/* Divider */}
      <div className="relative mb-10 w-full">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-[#E8EDF2]"></div>
        </div>
        <div className="relative flex justify-center text-[13px]">
          <span className="bg-white px-4 text-[#8B95A5] font-medium tracking-wide">or continue with</span>
        </div>
      </div>

      {/* Social Login */}
      <div className="grid grid-cols-3 gap-4 mb-12 w-full">
        <button type="button" className="flex items-center justify-center h-[52px] w-full rounded-[12px] border border-[#E8EDF2] bg-white hover:bg-[#F7F9FC] shadow-[0_2px_4px_rgba(17,19,26,0.02)] hover:shadow-[0_4px_12px_rgba(17,19,26,0.06)] transition-all duration-200">
          <svg viewBox="0 0 24 24" className="w-6 h-6" xmlns="http://www.w3.org/2000/svg"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/><path d="M1 1h22v22H1z" fill="none"/></svg>
        </button>
        <button type="button" className="flex items-center justify-center h-[52px] w-full rounded-[12px] border border-[#E8EDF2] bg-white hover:bg-[#F7F9FC] shadow-[0_2px_4px_rgba(17,19,26,0.02)] hover:shadow-[0_4px_12px_rgba(17,19,26,0.06)] transition-all duration-200">
          <svg viewBox="0 0 21 21" className="w-6 h-6" xmlns="http://www.w3.org/2000/svg"><path d="M10 0H0v10h10V0z" fill="#f25022"/><path d="M21 0H11v10h10V0z" fill="#7fba00"/><path d="M10 11H0v10h10V11z" fill="#00a4ef"/><path d="M21 11H11v10h10V11z" fill="#ffb900"/></svg>
        </button>
        <button type="button" className="flex items-center justify-center h-[52px] w-full rounded-[12px] border border-[#E8EDF2] bg-white hover:bg-[#F7F9FC] shadow-[0_2px_4px_rgba(17,19,26,0.02)] hover:shadow-[0_4px_12px_rgba(17,19,26,0.06)] transition-all duration-200">
          <svg viewBox="0 0 24 24" className="w-6 h-6" xmlns="http://www.w3.org/2000/svg"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.04 2.26-.87 3.52-.77 1.25.04 2.22.46 2.92 1.12-2.58 1.48-2.11 4.7.42 5.64-1.21 3.2-1.63 4.2-1.94 6.18zm-2.66-14.8c.45-1.4.15-2.73-.8-3.66-1.12-.98-2.63-1.03-3.18-1.02-.34 1.45.16 2.8 1.05 3.66.86.85 2.37 1.06 2.93 1.02z" fill="#000000"/></svg>
        </button>
      </div>

      <p className="text-[15px] text-[#5B6473] font-medium w-full text-center">
        Don&apos;t have an account?{" "}
        <a href="/register" className="font-bold text-[#0066FF] hover:text-[#0055D4] transition-colors">
          Sign up
        </a>
      </p>
    </div>
  );
}