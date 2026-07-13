"use client";

import { Mail, User } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { PasswordField } from "./PasswordField";
import { useRegister } from "../hooks/useRegister";

export function RegisterForm() {
  const {
    register,
    handleSubmit,
    onSubmit,
    errors,
    loading,
  } = useRegister();

  return (
    <div className="w-full flex flex-col">
      {/* Heading */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-[#11131A] font-[family-name:var(--font-space-grotesk)] tracking-tight">
          Create account
        </h2>
        <p className="text-[#5B6473] text-base mt-2">
          Start making intelligent investment decisions
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="w-full flex flex-col" noValidate>
        {/* Full Name */}
        <div className="mb-5">
          <label className="block text-sm font-semibold text-[#11131A] mb-2">
            Full Name
          </label>
          <div className="relative">
            <div className="pointer-events-none absolute inset-y-0 left-4 flex items-center text-[#8B95A5]">
              <User size={18} />
            </div>
            <Input
              placeholder="John Doe"
              className="!pl-[42px]"
              {...register("full_name")}
            />
          </div>
          {errors.full_name && (
            <p className="text-[13px] font-medium text-[#FF3B3B] mt-2">
              {errors.full_name.message}
            </p>
          )}
        </div>

        {/* Email */}
        <div className="mb-5">
          <label className="block text-sm font-semibold text-[#11131A] mb-2">
            Email Address
          </label>
          <div className="relative">
            <div className="pointer-events-none absolute inset-y-0 left-4 flex items-center text-[#8B95A5]">
              <Mail size={18} />
            </div>
            <Input
              type="email"
              placeholder="name@example.com"
              className="!pl-[42px]"
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
        <div className="mb-8">
          <PasswordField
            register={register}
            error={errors.password?.message}
          />
        </div>

        {/* Submit */}
        <Button
          type="submit"
          loading={loading}
          size="lg"
          fullWidth
          className="mb-8"
        >
          Create Account
        </Button>
      </form>

      <p className="text-[15px] text-[#5B6473] w-full text-center">
        Already have an account?{" "}
        <a href="/login" className="font-semibold text-[#0066FF] hover:text-[#0055D4] transition-colors">
          Sign in
        </a>
      </p>
    </div>
  );
}