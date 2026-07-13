import { NextRequest } from "next/server";
import { NextResponse } from "next/server";

export function middleware(

  request: NextRequest,

){

  const token=

    request.cookies.get(

      "access_token"

    );

  const path=

    request.nextUrl.pathname;

  const authPages=[

    "/login",

    "/register",

  ];

  if(

    authPages.includes(path)

    &&

    token

  ){

    return NextResponse.redirect(

      new URL(

        "/dashboard",

        request.url,

      )

    );

  }

  if(

    !authPages.includes(path)

    &&

    !token

  ){

    return NextResponse.redirect(

      new URL(

        "/login",

        request.url,

      )

    );

  }

  return NextResponse.next();

}

export const config={

matcher:[

"/",

"/dashboard/:path*",

"/prediction/:path*",

"/analytics/:path*",

"/history/:path*",

"/backtesting/:path*",

"/stocks/:path*",

"/login",

"/register",

],

};