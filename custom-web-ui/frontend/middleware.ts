import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

const INTERNAL_API_URL = process.env.INTERNAL_API_URL?.replace(/\/$/, "") ?? "";

export async function middleware(request: NextRequest) {
  const cookieHeader = request.headers.get("cookie") ?? "";

  if (!INTERNAL_API_URL) {
    if (!request.cookies.get("kh_session")) {
      return NextResponse.redirect(new URL("/login", request.url));
    }
    return NextResponse.next();
  }

  const meUrl = `${INTERNAL_API_URL}/api/auth/me`;
  const res = await fetch(meUrl, {
    headers: { cookie: cookieHeader },
    cache: "no-store",
  });

  if (res.ok) {
    return NextResponse.next();
  }

  return NextResponse.redirect(new URL("/login", request.url));
}

export const config = {
  matcher: [
    "/((?!api|login|_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
