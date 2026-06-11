import type { Metadata } from "next";
import { Bricolage_Grotesque, Schibsted_Grotesk, Caveat } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { QueryProvider } from "@/lib/query-provider";

// ALMANAC type system:
//  - display  → Bricolage Grotesque (characterful humanist grotesk, light weights)
//  - sans     → Schibsted Grotesk (the workhorse, Arket-like humanist sans)
//  - script   → Caveat (Marco's handwritten signature only)
const bricolage = Bricolage_Grotesque({
  weight: ["300", "400", "500", "600"],
  subsets: ["latin"],
  variable: "--font-bricolage",
  display: "swap",
});

const schibsted = Schibsted_Grotesk({
  weight: ["400", "500", "700"],
  subsets: ["latin"],
  variable: "--font-schibsted",
  display: "swap",
});

const caveat = Caveat({
  weight: ["500"],
  subsets: ["latin"],
  variable: "--font-caveat",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Marco",
  description: "Your AI cycling coach",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${bricolage.variable} ${schibsted.variable} ${caveat.variable}`}
    >
      <body className="min-h-screen bg-vb-bg font-sans text-vb-text antialiased">
        <QueryProvider>
          <AuthProvider>{children}</AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
