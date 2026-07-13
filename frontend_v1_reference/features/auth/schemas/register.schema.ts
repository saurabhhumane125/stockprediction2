import { z } from "zod";

export const registerSchema = z.object({

  full_name: z
    .string()
    .trim()
    .min(3, "Full name is required."),

  email: z
    .email("Enter a valid email address."),

  password: z
    .string()
    .min(8, "Password must contain at least 8 characters.")
    .regex(
      /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$/,
      "Password must contain uppercase, lowercase and a number."
    ),

});

export type RegisterSchema =
  z.infer<typeof registerSchema>;