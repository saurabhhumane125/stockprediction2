import type { ReactNode } from "react";

import { Card } from "@/components/ui/Card";

interface StatCardProps {

  title: string;

  value: string | number;

  icon?: ReactNode;

  description?: string;

}

export function StatCard({

  title,

  value,

  icon,

  description,

}: StatCardProps) {

  return (

    <Card
      className="
        h-full
      "
    >

      <div className="flex items-start justify-between">

        <div>

          <p

            className="
              text-sm
              font-medium
              text-[#5B6473]
            "

          >

            {title}

          </p>

          <h2

            className="
              mt-3
              text-4xl
              font-bold
              text-[#11131A]
            "

          >

            {value}

          </h2>

          {

            description && (

              <p

                className="
                  mt-2
                  text-sm
                  text-[#5B6473]
                "

              >

                {description}

              </p>

            )

          }

        </div>

        {

          icon && (

            <div

              className="
                rounded-2xl
                bg-[#EDF1F5]
                p-3
              "

            >

              {icon}

            </div>

          )

        }

      </div>

    </Card>

  );

}