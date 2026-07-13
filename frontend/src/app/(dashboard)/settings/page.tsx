"use client"

import * as React from "react"
import { Loader2, User, Mail, ShieldCheck, KeyRound } from "lucide-react"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useSettings } from "@/features/settings/hooks/useSettings"
import { useTheme } from "next-themes"

export default function SettingsPage() {
  const { data, loading, error, logout } = useSettings()
  const { theme, setTheme } = useTheme()

  if (loading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <p className="text-destructive font-medium">{error}</p>
      </div>
    )
  }

  const user = data?.user

  return (
    <div className="space-y-6 max-w-4xl animate-in fade-in slide-in-from-bottom-4 duration-500 ease-out">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-2">
          Manage your account settings and preferences.
        </p>
      </div>

      <div className="grid gap-6">
        <Card className="hover:border-primary/50 transition-colors">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5 text-primary" />
              Profile Information
            </CardTitle>
            <CardDescription>
              Your personal account details.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-1">
                <p className="text-sm font-medium text-muted-foreground">Full Name</p>
                <p className="text-base font-semibold">{user?.fullName}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Mail className="w-4 h-4" /> Email Address
                </p>
                <p className="text-base font-semibold">{user?.email}</p>
              </div>
            </div>
            
            <div className="pt-4 border-t border-border/50 flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-emerald-500 font-medium">
                <ShieldCheck className="w-4 h-4" />
                Account is Active
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <KeyRound className="w-4 h-4" />
                ID: {user?.id}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:border-primary/50 transition-colors">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-primary" />
              Preferences
            </CardTitle>
            <CardDescription>
              Customize your dashboard experience.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-base">Appearance</p>
                <p className="text-sm text-muted-foreground">Toggle between light and dark mode</p>
              </div>
              <Button 
                variant="outline" 
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              >
                {theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="border-destructive/20 hover:border-destructive/50 transition-colors">
          <CardHeader>
            <CardTitle className="text-destructive">Danger Zone</CardTitle>
            <CardDescription>
              Actions that will affect your authentication state.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="destructive" onClick={logout}>
              Sign Out of all sessions
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
