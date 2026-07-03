"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LogOut, Menu, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth-context";

/**
 * ALMANAC sidebar — a quiet masthead, a route-contour motif, and a calm
 * dotted nav. The active item is marked by a small forest dot, not a loud
 * underline. Editorial restraint over visual frills.
 */

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/dashboard/coach", label: "Coach Marco" },
  { href: "/dashboard/brain", label: "Your Brain" },
  { href: "/dashboard/rides", label: "Rides" },
  { href: "/dashboard/performance", label: "Performance" },
  { href: "/dashboard/goals", label: "Goals" },
  { href: "/dashboard/training", label: "Training" },
  { href: "/dashboard/settings", label: "Settings" },
];

function RouteMotif() {
  return (
    <svg
      className="mt-4 block text-vb-forest/60"
      width="150"
      height="14"
      viewBox="0 0 150 14"
      fill="none"
      aria-hidden
    >
      <path
        d="M0,10 C14,10 19,4 30,5 C43,6 47,11 60,10 C73,9 77,2 90,4 C103,6 109,10 122,9 C133,8 140,8 150,6"
        stroke="currentColor"
        strokeWidth="1.3"
        strokeLinecap="round"
      />
      <circle cx="150" cy="6" r="2.2" fill="var(--color-vb-clay)" />
    </svg>
  );
}

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
      <div className="px-7 pt-10 pb-2">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="font-display text-[22px] font-medium leading-none tracking-[0.22em]">
              MARCO
            </h1>
            <p className="mt-2.5 text-[10px] font-medium uppercase tracking-[0.18em] text-vb-text-muted">
              Your coach — life &amp; legs
            </p>
            <RouteMotif />
          </div>
          <button
            onClick={() => setMobileOpen(false)}
            className="text-vb-text-muted hover:text-vb-text md:hidden"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-5 py-8">
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
                    "flex items-center gap-3.5 rounded-sm px-3 py-2.5 text-[15px] transition-colors",
                    isActive
                      ? "text-vb-text"
                      : "text-vb-text-dim hover:text-vb-text"
                  )}
                >
                  <span
                    className={cn(
                      "h-1.5 w-1.5 rounded-full transition-colors",
                      isActive ? "bg-vb-forest" : "bg-vb-border"
                    )}
                  />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* User footer */}
      <div className="mx-5 mb-6 flex items-center justify-between gap-3 border-t border-vb-border-subtle pt-5">
        <div className="flex min-w-0 items-center gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-vb-forest font-display text-sm font-medium text-white">
            {(user?.full_name?.[0] || "R").toUpperCase()}
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium leading-none text-vb-text">
              {user?.full_name?.split(" ")[0] || "Rider"}
            </p>
            {user?.ftp && (
              <p className="mt-1 text-xs text-vb-text-muted">
                FTP · <span className="text-vb-text-dim">{user.ftp}w</span>
              </p>
            )}
          </div>
        </div>
        <button
          onClick={logout}
          className="rounded-sm border border-vb-border-subtle p-2 text-vb-text-muted transition-colors hover:border-vb-border hover:text-vb-text"
          title="Log out"
          aria-label="Log out"
        >
          <LogOut className="h-4 w-4" />
        </button>
      </div>
    </>
  );

  return (
    <>
      {/* Mobile header bar */}
      <div className="fixed inset-x-0 top-0 z-40 flex h-14 items-center gap-4 border-b border-vb-border-subtle bg-vb-bg px-4 md:hidden">
        <button
          onClick={() => setMobileOpen(true)}
          className="text-vb-text"
          aria-label="Open menu"
        >
          <Menu className="h-6 w-6" />
        </button>
        <span className="font-display text-lg font-medium tracking-[0.18em]">MARCO</span>
      </div>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-50 bg-vb-text/30 backdrop-blur-sm md:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-vb-border-subtle bg-vb-bg transition-transform duration-300 ease-in-out md:static md:z-auto md:w-64 md:translate-x-0",
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {sidebarContent}
      </aside>
    </>
  );
}
