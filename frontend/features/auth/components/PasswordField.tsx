"use client";

import { useState } from "react";

import {

  Eye,

  EyeOff,

  Lock,

} from "lucide-react";

import { Input } from "@/components/ui/Input";

interface Props {

  register: any;

  error?: string;

}

export function PasswordField({

  register,

  error,

}: Props) {

  const [

    visible,

    setVisible,

  ] = useState(false);

  return (

    <div className="space-y-2">

      <label

        className="
          text-sm
          font-semibold
          text-[#11131A]
        "

      >

        Password

      </label>

      <div className="relative">

        <Lock

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

          type={

            visible

              ? "text"

              : "password"

          }

          placeholder="Enter your password"

          className="px-12"

          {...register("password")}

        />

        <button

          type="button"

          onClick={() =>

            setVisible(!visible)

          }

          className="
            absolute
            right-4
            top-1/2
            -translate-y-1/2
            text-[#5B6473]
            hover:text-[#0066FF]
          "

        >

          {

            visible

              ? <EyeOff size={18}/>

              : <Eye size={18}/>

          }

        </button>

      </div>

      {

        error && (

          <p className="text-sm text-[#FF3B3B]">

            {error}

          </p>

        )

      }

    </div>

  );

}