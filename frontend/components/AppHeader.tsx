"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { getToken } from "@/lib/api";

const navigation = [
  { href: "/dashboard", label: "Evidence Library" },
  { href: "/upload", label: "Upload Evidence" },
  { href: "/history", label: "Review History" },
];

export function AppHeader() {
  const pathname = usePathname();
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    setAuthenticated(Boolean(getToken()));
  }, [pathname]);

  return (
    <header className="topbar">
      <div className="topbar-inner">
        <Link
          aria-label="AccrediLens home"
          className="brand"
          href={authenticated ? "/dashboard" : "/login"}
        >
          <span className="brand-mark" aria-hidden="true">
            A
          </span>

          <span className="brand-copy">
            <strong>AccrediLens</strong>
            <small>Accreditation Evidence Intelligence</small>
          </span>
        </Link>

        {authenticated ? (
          <nav aria-label="Primary navigation">
            {navigation.map((item) => (
              <Link
                className={pathname === item.href ? "nav-link active" : "nav-link"}
                href={item.href}
                key={item.href}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        ) : (
          <span className="trust-label">Evidence-led institutional review</span>
        )}
      </div>
    </header>
  );
}
