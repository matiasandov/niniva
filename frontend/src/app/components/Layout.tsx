import { Outlet, NavLink } from "react-router";
import { Activity, Users, Home, Mic, Stethoscope, Menu, X } from "lucide-react";
import { useState } from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { useLang } from "../context/LanguageContext";
import { useT } from "../i18n/translations";

function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

export function Layout() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { lang, setLang } = useLang();
  const t = useT(lang);

  const navItems = [
    { name: t.nav.dashboard, path: "/", icon: Home },
    { name: t.nav.liveSession, path: "/live", icon: Mic },
    { name: t.nav.motorTests, path: "/tests", icon: Activity },
    { name: t.nav.patients, path: "/patients", icon: Users },
  ];

  return (
    <div className="flex h-screen w-full bg-slate-50 text-slate-900 font-sans">
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-slate-900/50 z-40 md:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      <aside className={cn(
        "fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-slate-200 transform transition-transform duration-200 ease-in-out md:relative md:translate-x-0 flex flex-col",
        isMobileMenuOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="p-6 flex items-center justify-between">
          <div className="flex items-center gap-2 text-teal-600">
            <Stethoscope className="w-8 h-8" />
            <span className="text-2xl font-bold tracking-tight">Niniva</span>
          </div>
          <button className="md:hidden text-slate-500" onClick={() => setIsMobileMenuOpen(false)}>
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Language toggle */}
        <div className="px-4 pb-3">
          <div className="flex items-center gap-1 bg-slate-100 rounded-lg p-1 w-fit">
            <button
              onClick={() => setLang("en")}
              className={cn(
                "px-3 py-1 rounded-md text-sm font-semibold transition-all",
                lang === "en"
                  ? "bg-white text-teal-700 shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
              )}
            >
              EN
            </button>
            <button
              onClick={() => setLang("es")}
              className={cn(
                "px-3 py-1 rounded-md text-sm font-semibold transition-all",
                lang === "es"
                  ? "bg-white text-teal-700 shadow-sm"
                  : "text-slate-500 hover:text-slate-700"
              )}
            >
              ES
            </button>
          </div>
        </div>

        <div className="px-4 py-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
          {lang === "en" ? "Main Menu" : "Menú Principal"}
        </div>

        <nav className="flex-1 px-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg font-medium transition-colors",
                isActive
                  ? "bg-teal-50 text-teal-700"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              )}
              onClick={() => setIsMobileMenuOpen(false)}
            >
              <item.icon className="w-5 h-5" />
              {item.name}
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-100">
          <div className="flex items-center gap-3 px-3 py-2">
            <div className="w-8 h-8 rounded-full bg-teal-100 flex items-center justify-center text-teal-700 font-bold">
              Dr
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold text-slate-900">{t.nav.doctor}</span>
              <span className="text-xs text-slate-500">{t.nav.neurologist}</span>
            </div>
          </div>
        </div>
      </aside>

      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <header className="md:hidden flex items-center justify-between p-4 bg-white border-b border-slate-200">
          <div className="flex items-center gap-2 text-teal-600">
            <Stethoscope className="w-6 h-6" />
            <span className="text-xl font-bold">Niniva</span>
          </div>
          <button className="text-slate-500" onClick={() => setIsMobileMenuOpen(true)}>
            <Menu className="w-6 h-6" />
          </button>
        </header>

        <div className="flex-1 overflow-auto p-4 md:p-8">
          <div className="max-w-6xl mx-auto h-full">
            <Outlet />
          </div>
        </div>
      </main>
    </div>
  );
}
