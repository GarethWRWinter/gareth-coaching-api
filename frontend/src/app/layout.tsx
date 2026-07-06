import type { Metadata } from "next";
import { Archivo, Inter_Tight, IBM_Plex_Mono, Caveat } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { QueryProvider } from "@/lib/query-provider";

// FORMA type system:
//  - display  → Archivo (the wordmark / headline face)
//  - sans     → Inter Tight (the workhorse body face)
//  - mono     → IBM Plex Mono (labels, kickers, data)
//  - script   → Caveat (the coach's handwritten signature only)
const archivo = Archivo({
  weight: ["400", "500", "600", "700", "800"],
  subsets: ["latin"],
  variable: "--font-archivo",
  display: "swap",
});

const interTight = Inter_Tight({
  weight: ["400", "500", "600"],
  subsets: ["latin"],
  variable: "--font-inter-tight",
  display: "swap",
});

const plexMono = IBM_Plex_Mono({
  weight: ["400", "500", "600"],
  subsets: ["latin"],
  variable: "--font-plex-mono",
  display: "swap",
});

const caveat = Caveat({
  weight: ["500"],
  subsets: ["latin"],
  variable: "--font-caveat",
  display: "swap",
});

export const metadata: Metadata = {
  title: "FORMA",
  description: "A cycling coach with a memory",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`${archivo.variable} ${interTight.variable} ${plexMono.variable} ${caveat.variable}`}
    >
      <body className="min-h-screen bg-vb-bg font-sans text-vb-text antialiased">
        <QueryProvider>
          <AuthProvider>{children}</AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
