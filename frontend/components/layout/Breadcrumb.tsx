"use client";

import Link from "next/link";

import { ChevronRight } from "lucide-react";

interface BreadcrumbProps {

  items: {

    label: string;

    href?: string;

  }[];

}

export function Breadcrumb({

  items,

}: BreadcrumbProps) {

  return (

    <nav className="flex items-center gap-2 text-sm">

      {

        items.map((item,index)=>(

          <div
            key={item.label}
            className="flex items-center gap-2"
          >

            {

              item.href ? (

                <Link

                  href={item.href}

                  className="
                    text-[#5B6473]
                    transition
                    hover:text-[#0066FF]
                  "

                >

                  {item.label}

                </Link>

              ) : (

                <span
                  className="
                    font-semibold
                    text-[#11131A]
                  "
                >

                  {item.label}

                </span>

              )

            }

            {

              index!==items.length-1&&(

                <ChevronRight
                  size={16}
                  className="text-[#C3CCD8]"
                />

              )

            }

          </div>

        ))

      }

    </nav>

  );

}