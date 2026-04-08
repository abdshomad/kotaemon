#!/usr/bin/env python3
"""Find free TCP ports for local Next + FastAPI (custom-web-ui)."""

from __future__ import annotations

import argparse
import json
import socket
import sys


def port_is_free(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
        except OSError:
            return False
    return True


def next_free_port(host: str, start: int, *, max_tries: int = 2000) -> int:
    for port in range(start, start + max_tries):
        if port_is_free(host, port):
            return port
    print(f"error: no free port in [{start}, {start + max_tries})", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--host", default="127.0.0.1", help="Bind host to probe (default 127.0.0.1)")
    p.add_argument("--frontend-start", type=int, default=3000, help="First candidate for Next.js")
    p.add_argument("--backend-start", type=int, default=8000, help="First candidate for FastAPI")
    p.add_argument(
        "--json",
        action="store_true",
        help='Print {"frontend":N,"backend":M} only',
    )
    args = p.parse_args()

    frontend = next_free_port(args.host, args.frontend_start)
    backend = next_free_port(args.host, args.backend_start)
    if backend == frontend:
        backend = next_free_port(args.host, backend + 1)

    if args.json:
        print(json.dumps({"frontend": frontend, "backend": backend}))
        return

    base_fe = f"http://{args.host}:{frontend}"
    base_be = f"http://{args.host}:{backend}"
    lines = [
        f"CUSTOM_WEB_UI_HOST={args.host}",
        f"CUSTOM_WEB_UI_FRONTEND_PORT={frontend}",
        f"CUSTOM_WEB_UI_BACKEND_PORT={backend}",
        f"API_PROXY_TARGET={base_be}",
        f"INTERNAL_API_URL={base_be}",
        f"PLAYWRIGHT_BASE_URL={base_fe}",
    ]
    print("\n".join(lines) + "\n", end="")


if __name__ == "__main__":
    main()
