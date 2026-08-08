import type { Metadata } from "next";
import { AppHeader } from "@/components/AppHeader";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "AccrediLens",
    template: "%s | AccrediLens",
  },
  description:
    "AI-powered accreditation evidence intelligence for traceable institutional review.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AppHeader />
        <main className="shell">{children}</main>
      </body>
    </html>
  );
}
