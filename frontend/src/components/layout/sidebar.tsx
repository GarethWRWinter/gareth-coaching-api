"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LogOut, Menu, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";

/**
 * VoiceBox sidebar — magazine masthead + tracked-out nav.
 *
 * No iconography per nav item: the editorial language is built on type,
 * not visual frills. Active item gets a 3px red underline. User footer
 * shows FTP in mono numerals.
 */

const navItems = [
  { href: "/dashboard", label: "Today" },
  { href: "/dashboard/rides", label: "Rides" },
  { href: "/dashboard/performance", label: "Performance" },
  { href: "/dashboard/goals", label: "Goals" },
  { href: "/dashboard/training", label: "Training" },
  { href: "/dashboard/coach", label: "Coach" },
  { href: "/dashboard/settings", label: "Settings" },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  const sidebarContent = (
    <>
      {/* Masthead */}
      <div className="border-b-[3px] border-vb-text px-6 pt-6 pb-5">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="font-display text-4xl leading-none tracking-tight">
              MARCO
            </h1>
            <p className="mt-2 text-[10px] font-bold uppercase tracking-[0.18em] text-vb-text-dim">
              Issue 47 · Your Coach
            </p>
          </div>
          <button
            onClick={() => setMobileOpen(false)}
            className="text-vb-text-dim hover:text-vb-text md:hidden"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-6 py-6">
        <p className="mb-4 text-[10px] font-bold uppercase tracking-[0.18em] text-vb-text-muted">
          Sections
        </p>
        <ul className="space-y-1">
          {navItems.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== "/dashboard" && pathname.startsWith(item.href));

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "block py-2 text-sm font-bold uppercase tracking-[0.10em] transition-colors",
                    isActive
                      ? "text-vb-text"
                      : "text-vb-text-dim hover:text-vb-text"
                  )}
                >
                  <span className={cn(
                    "inline-block",
                    isActive && "border-b-[3px] border-vb-red pb-[2px]"
                  )}>
                    {item.label}
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* User footer */}
      <div className="border-t-2 border-vb-border-subtle px-6 py-5">
        <div className="flex items-center justify-between gap-3">
          <div className="min-w-0">
            <p className="truncate font-display text-lg leading-none">
              {user?.full_name?.split(" ")[0] || "Rider"}
            </p>
            {user?.ftp && (
              <p className="mt-1.5 font-mono text-xs text-vb-text-dim">
                FTP · <span className="text-vb-text">{user.ftp}W</span>
              </p>
            )}
          </div>
          <button
            onClick={logout}
            className="border-2 border-vb-border-subtle p-2 text-vb-text-dim transition-colors hover:border-vb-text hover:text-vb-text"
            title="Log out"
            aria-label="Log out"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile header bar */}
      <div className="fixed inset-x-0 top-0 z-40 flex h-14 items-center gap-4 border-b-2 border-vb-text bg-vb-bg px-4 md:hidden">
        <button
          onClick={() => setMobileOpen(true)}
          className="text-vb-text"
          aria-label="Open menu"
        >
          <Menu className="h-6 w-6" />
        </button>
        <span className="font-display text-xl leading-none">MARCO</span>
      </div>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-50 bg-vb-bg/90 backdrop-blur-sm md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r-2 border-vb-border-subtle bg-vb-bg transition-transform duration-300 ease-in-out md:static md:z-auto md:w-64 md:translate-x-0",
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {sidebarContent}
      </aside>
    </>
  );
}
