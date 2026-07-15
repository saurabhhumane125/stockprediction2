"use client"

import * as React from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Loader2, TrendingUp } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { authApi } from "@/lib/api/auth"

const registerSchema = z.object({
  full_name: z.string().min(2, "Name must be at least 2 characters."),
  email: z.string().email("Please enter a valid email address."),
  password: z.string().min(8, "Password must be at least 8 characters."),
})

type RegisterFormValues = z.infer<typeof registerSchema>

export default function RegisterPage() {
  const router = useRouter()
  const [error, setError] = React.useState<string | null>(null)
  
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  })

  async function onSubmit(data: RegisterFormValues) {
    try {
      setError(null)
      await authApi.register(data)
      
      // Auto-login after registration (if backend supports it, otherwise redirect to login)
      try {
        const res = await authApi.login({ email: data.email, password: data.password })
        if (res.message) {
          localStorage.setItem("auth_token", "cookie_set")
          router.push("/dashboard")
        } else {
          router.push("/login")
        }
      } catch (e) {
        router.push("/login")
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "An error occurred during registration.")
    }
  }

  return (
    <div className="flex flex-col space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 ease-out w-full max-w-sm mx-auto">
      <div className="flex flex-col space-y-2 text-center md:text-left">
        <div className="flex items-center justify-center md:hidden gap-2 mb-6 text-primary">
          <TrendingUp className="w-8 h-8" />
          <span className="text-xl font-bold tracking-tight text-foreground">TradePredict</span>
        </div>
        <h2 className="text-3xl font-semibold tracking-tight text-foreground">Create an account</h2>
        <p className="text-sm text-muted-foreground">
          Enter your details below to create your account
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
            <label className="text-sm font-medium leading-none text-foreground" htmlFor="full_name">
              Full Name
            </label>
            <Input
              id="full_name"
              placeholder="John Doe"
              autoCapitalize="words"
              disabled={isSubmitting}
              className="bg-white"
              {...register("full_name")}
            />
            {errors.full_name && (
              <p className="text-xs text-destructive">{errors.full_name.message}</p>
            )}
          </div>
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
          Create Account
        </Button>
      </form>

      <div className="text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-primary hover:underline underline-offset-4 transition-colors">
          Sign in
        </Link>
      </div>
    </div>
  )
}
