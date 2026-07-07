import type { ReactNode } from "react";

import { Breadcrumb } from "./Breadcrumb";

interface PageHeaderProps {

  title: string;

  subtitle?: string;

  actions?: ReactNode;

  breadcrumbs?: {

    label: string;

    href?: string;

  }[];

}

export function PageHeader({

  title,

  subtitle,

  actions,

  breadcrumbs,

}: PageHeaderProps) {

  return (

    <section className="mb-10">

      {

        breadcrumbs && (

          <Breadcrumb

            items={breadcrumbs}

          />

        )

      }

      <div

        className="
          mt-3
          flex
          flex-col
          gap-5
          lg:flex-row
          lg:items-end
          lg:justify-between
        "

      >

        <div>

          <h1

            className="
              text-4xl
              font-bold
              tracking-tight
              text-[#11131A]
            "

          >

            {title}

          </h1>

          {

            subtitle && (

              <p

                className="
                  mt-3
                  max-w-2xl
                  text-base
                  leading-7
                  text-[#5B6473]
                "

              >

                {subtitle}

              </p>

            )

          }

        </div>

        {

          actions && (

            <div>

              {actions}

            </div>

          )

        }

      </div>

    </section>

  );

}