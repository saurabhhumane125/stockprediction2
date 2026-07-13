"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Loader2, TrendingUp } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { authApi } from "@/lib/api/auth"

const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address."),
  password: z.string().min(8, "Password must be at least 8 characters."),
})

type LoginFormValues = z.infer<typeof loginSchema>

export default function LoginPage() {
  const router = useRouter()
  const [error, setError] = React.useState<string | null>(null)
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  })

  async function onSubmit(data: LoginFormValues) {
    try {
      setError(null)
      const res = await authApi.login(data)
      // Backend sets an HttpOnly cookie, we just need to verify it was successful
      if (res.message) {
        // Also we don't strictly need to set an auth_token in local storage if it's HttpOnly, 
        // but we can set a flag that we are logged in, or just redirect.
        localStorage.setItem("auth_token", "cookie_set") 
        router.push("/dashboard")
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Invalid email or password.")
    }
  }

  return (
    <div className="flex flex-col space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 ease-out w-full max-w-sm mx-auto">
      <div className="flex flex-col space-y-2 text-center md:text-left">
        <div className="flex items-center justify-center md:hidden gap-2 mb-6 text-primary">
          <TrendingUp className="w-8 h-8" />
          <span className="text-xl font-bold tracking-tight text-foreground">TradePredict</span>
        </div>
        <h2 className="text-3xl font-semibold tracking-tight text-foreground">Welcome back</h2>
        <p className="text-sm text-muted-foreground">
          Enter your credentials to access your account
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {error && (
          <div className="p-3 text-sm font-medium text-destructive bg-destructive/10 rounded-md border border-destructive/20">
            {error}
          </div>
        )}
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium leading-none text-foreground" htmlFor="email">
              Email
            </label>
            <Input
              id="email"
              type="email"
              placeholder="name@example.com"
              autoCapitalize="none"
              autoComplete="email"
              autoCorrect="off"
              disabled={isSubmitting}
              className="bg-white"
              {...register("email")}
            />
            {errors.email && (
              <p className="text-xs text-destructive">{errors.email.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-sm font-medium leading-none text-foreground" htmlFor="password">
                Password
              </label>
            </div>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              autoComplete="current-password"
              disabled={isSubmitting}
              className="bg-white"
              {...register("password")}
            />
            {errors.password && (
              <p className="text-xs text-destructive">{errors.password.message}</p>
            )}
          </div>
        </div>
        <Button className="w-full shadow-sm" type="submit" disabled={isSubmitting}>
          {isSubmitting ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : null}
          Sign In
        </Button>
      </form>

      <div className="text-center text-sm text-muted-foreground">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="font-medium text-primary hover:underline underline-offset-4 transition-colors">
          Sign up
        </Link>
      </div>
    </div>
  )
}
