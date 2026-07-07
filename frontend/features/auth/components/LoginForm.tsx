"use client";

import { Mail } from "lucide-react";

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

    <form

      onSubmit={handleSubmit(onSubmit)}

      className="space-y-8"

    >

      <div>

        <p

          className="
            text-sm
            font-semibold
            uppercase
            tracking-[0.22em]
            text-[#0066FF]
          "

        >

          Welcome Back

        </p>

        <h1

          className="
            mt-3
            font-['Space_Grotesk']
            text-4xl
            font-bold
            text-[#11131A]
          "

        >

          Sign in

        </h1>

        <p

          className="
            mt-3
            text-base
            leading-7
            text-[#5B6473]
          "

        >

          Continue to your stock prediction workspace.

        </p>

      </div>

      <div className="space-y-2">

        <label

          className="
            text-sm
            font-semibold
            text-[#11131A]
          "

        >

          Email Address

        </label>

        <div className="relative">

          <Mail

            size={18}

            className="
              absolute
              left-4
              top-1/2
              -translate-y-1/2
              text-[#5B6473]
            "

          />

          <Input

            type="email"

            placeholder="name@example.com"

            className="pl-12"

            {...register("email")}

          />

        </div>

        {

          errors.email && (

            <p className="text-sm text-[#FF3B3B]">

              {errors.email.message}

            </p>

          )

        }

      </div>

      <PasswordField

        register={register}

        error={errors.password?.message}

      />

      <Button

        type="submit"

        size="lg"

        fullWidth

        loading={loading}

      >

        Sign In

      </Button>

    </form>

  );

}