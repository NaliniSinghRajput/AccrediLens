import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Local Intelligent LMS",
  description: "Local-first PDF grounded LMS"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <Link href="/dashboard" className="brand">Local Intelligent LMS</Link>
          <nav>
            <Link href="/upload">Upload</Link>
            <Link href="/dashboard">Library</Link>
            <Link href="/history">History</Link>
          </nav>
        </header>
        <main className="shell">{children}</main>
      </body>
    </html>
  );
}
